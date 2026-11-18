"""
Chay lai Baseline doi chung khop dung k cua tung nghiem NSGA-II da chon (Delta va Knee)
theo AGENTS.md Muc 4.2 va thuc hien kiem dinh Wilcoxon theo cap.
Luu toan bo ket qua vao results/v3_... (khong de len v2).
"""
import os
import sys
import subprocess
import numpy as np
import pandas as pd
from scipy import stats

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(ROOT_DIR, "data")
RESULTS_DIR = os.path.join(ROOT_DIR, "results")
PYTHON_EXE = sys.executable

# Bo sung data vao sys.path de import cac module chung neu can
if DATA_DIR not in sys.path:
    sys.path.insert(0, DATA_DIR)

SEEDS = [42, 43, 44, 45, 46, 47]

DATASETS = [
    {
        "name": "DataSense",
        "data_file": os.path.join(DATA_DIR, "datasense_10sec_processed.parquet"),
        "v2_prefix": "v2_ds",
        "v3_base_prefix": "v3_base_datasense",
    },
    {
        "name": "NF-UQ",
        "data_file": os.path.join(DATA_DIR, "nfuqnids_processed.parquet"),
        "v2_prefix": "v2_nfuq",
        "v3_base_prefix": "v3_base_nfuq",
    },
]

def run_command(cmd):
    env = os.environ.copy()
    env["PYTHONPATH"] = DATA_DIR + os.pathsep + env.get("PYTHONPATH", "")
    print(f"\n[EXEC] {' '.join(cmd)}")
    subprocess.run(cmd, env=env, check=True)

def get_target_ks(v2_dir):
    csv_path = os.path.join(v2_dir, "final_eval.csv")
    df = pd.read_csv(csv_path)
    delta_row = df[df["selected"].str.startswith("chosen_delta", na=False)].iloc[0]
    knee_row = df[df["selected"].str.startswith("knee", na=False)].iloc[0]
    k_delta = int(delta_row["n_features"])
    k_knee = int(knee_row["n_features"])
    return k_delta, k_knee, float(delta_row["test_macro_f1"]), float(knee_row["test_macro_f1"])

def run_baselines_for_dataset(ds_info):
    name = ds_info["name"]
    data_file = ds_info["data_file"]
    print(f"\n{'='*70}\n[1] CHAY BASELINES KHOP K CHO TAP DU LIEU: {name}\n{'='*70}")
    
    for s in SEEDS:
        v2_dir = os.path.join(RESULTS_DIR, f"{ds_info['v2_prefix']}_s{s}")
        outdir = os.path.join(RESULTS_DIR, f"{ds_info['v3_base_prefix']}_s{s}")
        k_delta, k_knee, _, _ = get_target_ks(v2_dir)
        ks = sorted(list(set([k_knee, k_delta])))
        ks_str = [str(k) for k in ks]
        
        summary_file = os.path.join(outdir, "baselines_summary.csv")
        if os.path.exists(summary_file):
            print(f"--> Da ton tai ket qua cho Seed {s} tai {outdir}, bo qua.")
            continue
            
        print(f"\n>>> Seed {s}: k_knee={k_knee}, k_delta={k_delta} -> ks={ks_str}")
        cmd = [
            PYTHON_EXE, "-u", os.path.join(DATA_DIR, "baselines.py"),
            "--data", data_file,
            "--outdir", outdir,
            "--seed", str(s),
            "--ks"
        ] + ks_str + [
            "--n_random", "20"
        ]
        run_command(cmd)

def run_wilcoxon_tests():
    print(f"\n{'='*70}\n[2] TIEN HANH KIEM DINH THONG KE WILCOXON THEO CAP (CUNG K, CUNG SEED)\n{'='*70}")
    all_results = []
    
    for ds_info in DATASETS:
        name = ds_info["name"]
        for sol_type in ["delta", "knee"]:
            # Thu thap diem theo seed
            seed_data = []
            for s in SEEDS:
                v2_dir = os.path.join(RESULTS_DIR, f"{ds_info['v2_prefix']}_s{s}")
                v3_dir = os.path.join(RESULTS_DIR, f"{ds_info['v3_base_prefix']}_s{s}")
                k_delta, k_knee, f1_delta, f1_knee = get_target_ks(v2_dir)
                
                target_k = k_delta if sol_type == "delta" else k_knee
                nsga2_f1 = f1_delta if sol_type == "delta" else f1_knee
                
                summary_df = pd.read_csv(os.path.join(v3_dir, "baselines_summary.csv"))
                sub = summary_df[summary_df["k"] == target_k]
                
                row_dict = {
                    "dataset": name,
                    "solution": sol_type,
                    "seed": s,
                    "k": target_k,
                    "nsga2": nsga2_f1,
                }
                for m in ["boruta_lite", "lgbm_imp", "mi", "random"]:
                    m_row = sub[sub["method"] == m]
                    if len(m_row) > 0:
                        row_dict[m] = float(m_row.iloc[0]["test_f1"])
                    else:
                        row_dict[m] = np.nan
                seed_data.append(row_dict)
                
            df_seed = pd.DataFrame(seed_data)
            print(f"\n--- {name} (Nghiem: {sol_type.upper()}) ---")
            print(df_seed[["seed", "k", "nsga2", "boruta_lite", "lgbm_imp", "mi", "random"]].to_string(index=False))
            
            # Tinh toan Wilcoxon
            nsga2_arr = df_seed["nsga2"].values
            for m in ["boruta_lite", "lgbm_imp", "mi", "random"]:
                base_arr = df_seed[m].values
                diff = nsga2_arr - base_arr
                mean_diff = float(np.mean(diff))
                
                # Wilcoxon signed-rank test
                # Khi n=6 va cac phan tu khac nhau, p-value toi thieu 1/32 = 0.03125
                try:
                    res = stats.wilcoxon(nsga2_arr, base_arr, alternative="two-sided")
                    stat = float(res.statistic)
                    pval = float(res.pvalue)
                except Exception as e:
                    stat = np.nan
                    pval = np.nan
                    
                all_results.append({
                    "dataset": name,
                    "solution_type": sol_type,
                    "n_seeds": len(SEEDS),
                    "baseline_method": m,
                    "mean_nsga2": float(np.mean(nsga2_arr)),
                    "mean_baseline": float(np.mean(base_arr)),
                    "mean_diff (nsga2 - base)": mean_diff,
                    "wilcoxon_stat": stat,
                    "p_value": pval,
                    "significant_0.05": pval < 0.05 if not np.isnan(pval) else False,
                    "significant_0.10": pval < 0.10 if not np.isnan(pval) else False,
                })
                
    df_wilcoxon = pd.DataFrame(all_results)
    out_csv = os.path.join(RESULTS_DIR, "v3_wilcoxon_summary.csv")
    df_wilcoxon.to_csv(out_csv, index=False)
    print(f"\n{'='*70}\nTONG HOP KET QUA KIEM DINH WILCOXON THEO CAP (LUU TAI {out_csv})\n{'='*70}")
    print(df_wilcoxon.to_string(index=False))

def main():
    print("="*70)
    print("BAT DAU BƯƠC 3: BASELINES KHOP K & KIEM DINH WILCOXON (NHOM 9)")
    print("="*70)
    
    # 1. Chay DataSense
    run_baselines_for_dataset(DATASETS[0])
    
    # 2. Chay NF-UQ
    run_baselines_for_dataset(DATASETS[1])
    
    # 3. Kiem dinh Wilcoxon
    run_wilcoxon_tests()
    
    print("\n=== HOAN TAT TOAN BO BƯOC 3 THANH CONG ===")

if __name__ == "__main__":
    main()
