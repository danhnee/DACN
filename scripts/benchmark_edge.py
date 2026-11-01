#!/usr/bin/env python3
"""
Benchmark latency and memory on edge-constrained environments (E1, E2)
Designed for HUTECH DACN - Nhom 9 (Nguyen Minh Nhat phu trach)
Warm-up: 10 runs, Measurements: 30 repetitions
Batch sizes: 1 (single-sample streaming) and 1024 (batch throughput)
"""
import os
import sys
import time
import argparse
import tracemalloc
import numpy as np
import pandas as pd
import lightgbm as lgb

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")))
from common import load_split, make_model

def set_hardware_profile(profile_name):
    """Set CPU affinity to simulate E1 (1 CPU) and E2 (2 CPUs)."""
    pid = os.getpid()
    if profile_name == "E1":
        os.sched_setaffinity(pid, {0})
        print("[Env] Hardware Profile: E1 (1 vCPU, core {0})")
    elif profile_name == "E2":
        os.sched_setaffinity(pid, {0, 1})
        print("[Env] Hardware Profile: E2 (2 vCPUs, cores {0, 1})")
    else:
        print(f"[Env] Hardware Profile: Unconstrained ({os.cpu_count()} CPUs)")

def benchmark_inference(model, X_test, feature_indices=None, batch_size=1, warmups=10, reps=30):
    """
    Measure inference latency (warm-up 10, reps 30) and memory peak using tracemalloc.
    """
    if feature_indices is not None:
        X_eval = X_test[:, feature_indices]
    else:
        X_eval = X_test

    n_samples = len(X_eval)
    if batch_size == 1:
        sample_pool = X_eval[:min(100, n_samples)]
        
        # Warm-up 10 runs
        for i in range(warmups):
            row = sample_pool[i % len(sample_pool)].reshape(1, -1)
            _ = model.predict(row)
            
        # Benchmark 30 runs
        latencies = []
        for i in range(reps):
            row = sample_pool[i % len(sample_pool)].reshape(1, -1)
            t0 = time.perf_counter()
            _ = model.predict(row)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0) # in ms
            
    else:
        n_eval = min(batch_size, n_samples)
        batch = X_eval[:n_eval]
        
        # Warm-up 10 runs
        for _ in range(warmups):
            _ = model.predict(batch)
            
        latencies = []
        for _ in range(reps):
            t0 = time.perf_counter()
            _ = model.predict(batch)
            t1 = time.perf_counter()
            latencies.append((t1 - t0) * 1000.0) # in ms

    # Measure RAM peak
    tracemalloc.start()
    _ = model.predict(X_eval[:min(batch_size, n_samples)])
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    median_lat = float(np.median(latencies))
    std_lat = float(np.std(latencies))
    peak_kb = peak / 1024.0

    return {
        "batch_size": batch_size,
        "median_ms": median_lat,
        "std_ms": std_lat,
        "peak_ram_kb": peak_kb
    }

def main():
    parser = argparse.ArgumentParser(description="Edge Benchmark for NIDS LightGBM")
    parser.add_argument("--data", default="data/datasense_10sec_processed.parquet", help="Path to parquet")
    parser.add_argument("--profile", choices=["E1", "E2", "DEV"], default="E1", help="Edge hardware profile")
    parser.add_argument("--out", default="results/edge_benchmark_summary.csv", help="Output summary file")
    args = parser.parse_args()

    set_hardware_profile(args.profile)

    print(f"Loading data from {args.data}...")
    feats, (Xtr, ytr, Xva, yva, Xte, yte), classes = load_split(args.data)
    print(f"Dataset loaded: {len(feats)} features, {len(classes)} classes. Test samples: {len(Xte)}")

    print("Training LightGBM model (150 trees fixed)...")
    clf = make_model(n_estimators=150, n_jobs=1 if args.profile == "E1" else 2, seed=42)
    clf.fit(Xtr, ytr)

    print("\nRunning Edge Benchmarks:")
    results = []
    for bs in [1, 1024]:
        res = benchmark_inference(clf, Xte, feature_indices=None, batch_size=bs, warmups=10, reps=30)
        res["profile"] = args.profile
        res["features"] = len(feats)
        results.append(res)
        print(f"  Profile={args.profile} | Batch={bs:4d} | Median={res['median_ms']:.3f} ms | Std={res['std_ms']:.3f} ms | Peak RAM={res['peak_ram_kb']:.1f} KB")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    df_res = pd.DataFrame(results)
    df_res.to_csv(args.out, index=False)
    print(f"\nSaved benchmark results to {args.out}")

if __name__ == "__main__":
    main()
