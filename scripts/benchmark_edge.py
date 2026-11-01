#!/usr/bin/env python3
"""
Standardized Edge Benchmark for NIDS LightGBM Models
Measures Latency (Median & IQR), Peak Memory RSS, and Model Size.
Hardware Profiles: E1 (1 vCPU, core 0), E2 (2 vCPUs, cores 0, 1)
"""
import os
import sys
import time
import json
import argparse
import subprocess
import resource
import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")))
try:
    from common import load_split, make_model
except ImportError:
    from data.common import load_split, make_model

def set_hardware_profile(profile_name):
    """Set CPU affinity to simulate E1 (1 CPU) and E2 (2 CPUs)."""
    pid = os.getpid()
    if profile_name == "E1":
        os.sched_setaffinity(pid, {0})
    elif profile_name == "E2":
        os.sched_setaffinity(pid, {0, 1})

def worker_measure(model_path, slice_path, profile, batch_size=1, warmups=10, reps=30):
    """
    Worker process: sets affinity, loads model, measures latency and peak RSS.
    """
    set_hardware_profile(profile)
    
    # Load test slice (5,000 samples)
    X_eval = np.load(slice_path)
    n_samples = len(X_eval)
    
    # Load model
    booster = lgb.Booster(model_file=model_path)
    
    latencies = []
    if batch_size == 1:
        sample_pool = X_eval[:min(100, n_samples)]
        # Warm-up
        for i in range(warmups):
            row = sample_pool[i % len(sample_pool)].reshape(1, -1)
            _ = booster.predict(row, n_jobs=1)
        # Benchmark
        for i in range(reps):
            row = sample_pool[i % len(sample_pool)].reshape(1, -1)
            t0 = time.perf_counter()
            _ = booster.predict(row, n_jobs=1)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)
    else:
        n_eval = min(batch_size, n_samples)
        batch = X_eval[:n_eval]
        # Warm-up
        for _ in range(warmups):
            _ = booster.predict(batch, n_jobs=1 if profile == "E1" else 2)
        # Benchmark
        for _ in range(reps):
            t0 = time.perf_counter()
            _ = booster.predict(batch, n_jobs=1 if profile == "E1" else 2)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0)

    # ru_maxrss is in Kilobytes on Linux
    peak_rss_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    
    lat_arr = np.array(latencies)
    median_ms = float(np.median(lat_arr))
    q75, q25 = np.percentile(lat_arr, [75, 25])
    iqr_ms = float(q75 - q25)
    
    out = {
        "median_ms": median_ms,
        "iqr_ms": iqr_ms,
        "peak_rss_kb": peak_rss_kb
    }
    print(json.dumps(out))

def run_worker_subproc(model_path, slice_path, profile, batch_size):
    cmd = [
        sys.executable, __file__,
        "--worker",
        "--model_path", model_path,
        "--slice_path", slice_path,
        "--profile", profile,
        "--batch_size", str(batch_size)
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return json.loads(res.stdout.strip())

def main():
    parser = argparse.ArgumentParser(description="Edge Benchmark Suite")
    parser.add_argument("--worker", action="store_true", help="Internal worker flag")
    parser.add_argument("--model_path", help="Path to saved model")
    parser.add_argument("--slice_path", help="Path to test slice")
    parser.add_argument("--profile", choices=["E1", "E2", "DEV"], default="E1")
    parser.add_argument("--batch_size", type=int, default=1)
    
    # Master arguments
    parser.add_argument("--data", default="data/datasense_10sec_processed.parquet")
    parser.add_argument("--label", default=None)
    parser.add_argument("--results_dir", default="results/ds_s42")
    parser.add_argument("--out", default="results/edge_benchmark_summary.csv")
    args = parser.parse_args()

    if args.worker:
        worker_measure(args.model_path, args.slice_path, args.profile, args.batch_size)
        return

    # Master controller
    print("="*70)
    print("CHUẨN HÓA BENCHMARK MÔI TRƯỜNG BIÊN E1 & E2 (ISOLATED SUBPROCESS)")
    print("="*70)
    
    feats, (Xtr, ytr, Xva, yva, Xte, yte), classes = load_split(args.data, args.label)
    d = len(feats)
    
    # Fixed random slice of 5,000 samples
    rng = np.random.default_rng(0)
    idx_te = rng.choice(len(Xte), min(5000, len(Xte)), replace=False)
    Xte_5k = np.ascontiguousarray(Xte[idx_te], dtype=np.float32)
    
    tmp_dir = "/tmp/bench_edge"
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Identify models to benchmark
    models_to_test = [
        ("all", np.ones(d, dtype=bool), d)
    ]
    
    # Add Pareto Knee or chosen solutions if final_eval.csv exists
    final_eval_path = os.path.join(args.results_dir, "final_eval.csv")
    if os.path.exists(final_eval_path):
        df_final = pd.read_csv(final_eval_path)
        # Knee solution
        knee_row = df_final[df_final["selected"].str.contains("knee_balanced", na=False)]
        if len(knee_row) > 0:
            k_feats = knee_row.iloc[0]["features"].split(";")
            mask_knee = np.array([f in k_feats for f in feats])
            if mask_knee.sum() > 0:
                models_to_test.append(("knee_balanced", mask_knee, int(mask_knee.sum())))
            
        # Delta solution
        delta_row = df_final[df_final["selected"].str.contains("chosen_delta", na=False)]
        if len(delta_row) > 0:
            d_feats = delta_row.iloc[0]["features"].split(";")
            mask_delta = np.array([f in d_feats for f in feats])
            if mask_delta.sum() > 0 and mask_delta.sum() != models_to_test[-1][2]:
                models_to_test.append(("chosen_delta", mask_delta, int(mask_delta.sum())))
    else:
        # Fallback: top 25 features
        mask_25 = np.zeros(d, dtype=bool)
        mask_25[:min(25, d)] = True
        models_to_test.append(("subset_k25", mask_25, int(mask_25.sum())))

    results = []
    for method, mask, k in models_to_test:
        print(f"\n--- Huấn luyện và xuất mô hình: {method} (k={k}/{d}) ---")
        clf = make_model(n_estimators=150, n_jobs=2, seed=42)
        clf.fit(Xtr[:, mask], ytr)
        
        # Save model
        model_path = os.path.join(tmp_dir, f"model_{method}_{k}.txt")
        clf.booster_.save_model(model_path)
        model_size_kb = round(os.path.getsize(model_path) / 1024.0, 2)
        
        # Save feature slice for this model
        slice_path = os.path.join(tmp_dir, f"slice_{method}_{k}.npy")
        np.save(slice_path, Xte_5k[:, mask])
        
        for profile in ["E1", "E2"]:
            for bs in [1, 1024]:
                res = run_worker_subproc(model_path, slice_path, profile, bs)
                row = {
                    "method": method,
                    "k": k,
                    "profile": profile,
                    "batch_size": bs,
                    "median_ms": round(res["median_ms"], 3),
                    "iqr_ms": round(res["iqr_ms"], 3),
                    "peak_rss_kb": res["peak_rss_kb"],
                    "model_size_kb": model_size_kb
                }
                results.append(row)
                print(f"  [{profile}] {method:13s} (k={k:2d}) | Batch={bs:4d} | Median={row['median_ms']:7.3f} ms | IQR={row['iqr_ms']:6.3f} ms | Peak RSS={row['peak_rss_kb']:6d} KB | Model={model_size_kb} KB")

    df_res = pd.DataFrame(results)
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df_res.to_csv(args.out, index=False)
    print(f"\n[OK] Đã lưu kết quả benchmark chi tiết vào: {args.out}")

if __name__ == "__main__":
    main()
