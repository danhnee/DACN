#!/usr/bin/env python3
"""
Diagnostic script to check data shortcuts, data leakage, and feature sanity:
1. Constant features (zero variance)
2. Train-Test exact duplicate feature vectors (DataSense and NF-UQ)
3. Single-feature predictive power (flag if single feature achieves high Macro-F1)
4. Ablation: performance when dropping 7 log_* features from DataSense
"""
import os
import sys
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.metrics import f1_score

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data")))
from common import load_split, make_model

def check_constant_features(name, Xtr, feats):
    stds = np.std(Xtr, axis=0)
    const_feats = [feats[i] for i, s in enumerate(stds) if s == 0]
    return const_feats

def check_train_test_duplicates(Xtr, ytr, Xte, yte):
    # Convert rows to bytes or hash for exact match
    df_tr = pd.DataFrame(Xtr)
    df_te = pd.DataFrame(Xte)
    
    # Find duplicate feature vectors in test that exist in train
    merged = df_te.merge(df_tr.drop_duplicates(), how='inner')
    # Count how many test rows match any train row
    # Use pandas merge with indicator
    df_tr_unique = df_tr.copy()
    df_tr_unique['in_tr'] = True
    df_tr_unique = df_tr_unique.drop_duplicates(subset=df_tr.columns[:])
    
    m = df_te.merge(df_tr_unique, how='left')
    n_dups = m['in_tr'].sum()
    pct = 100.0 * n_dups / len(Xte)
    return int(n_dups), len(Xte), pct

def check_single_features(Xtr, ytr, Xte, yte, feats, classes, threshold=0.75):
    flagged = []
    for i, f in enumerate(feats):
        clf = lgb.LGBMClassifier(n_estimators=60, learning_rate=0.08, n_jobs=2, random_state=42, verbose=-1)
        clf.fit(Xtr[:, [i]], ytr)
        preds = clf.predict(Xte[:, [i]])
        f1 = f1_score(yte, preds, labels=classes, average="macro", zero_division=0)
        if f1 >= threshold:
            flagged.append((f, f1))
    flagged.sort(key=lambda x: x[1], reverse=True)
    return flagged

def check_log_ablation(data_path):
    feats, (Xtr, ytr, Xva, yva, Xte, yte), classes = load_split(data_path)
    
    # 1. Full 71 features
    clf_all = make_model(n_estimators=150, seed=42)
    clf_all.fit(Xtr, ytr)
    pred_va_all = clf_all.predict(Xva)
    pred_te_all = clf_all.predict(Xte)
    f1_va_all = f1_score(yva, pred_va_all, labels=classes, average="macro", zero_division=0)
    f1_te_all = f1_score(yte, pred_te_all, labels=classes, average="macro", zero_division=0)
    
    # 2. No log features (only network_* features, 64 features)
    non_log_mask = np.array([not f.startswith("log_") for f in feats])
    clf_nolog = make_model(n_estimators=150, seed=42)
    clf_nolog.fit(Xtr[:, non_log_mask], ytr)
    pred_va_nolog = clf_nolog.predict(Xva[:, non_log_mask])
    pred_te_nolog = clf_nolog.predict(Xte[:, non_log_mask])
    f1_va_nolog = f1_score(yva, pred_va_nolog, labels=classes, average="macro", zero_division=0)
    f1_te_nolog = f1_score(yte, pred_te_nolog, labels=classes, average="macro", zero_division=0)
    
    return {
        "all_71": (f1_va_all, f1_te_all),
        "no_log_64": (f1_va_nolog, f1_te_nolog),
        "diff_val": f1_va_all - f1_va_nolog,
        "diff_test": f1_te_all - f1_te_nolog
    }

def main():
    print("="*70)
    print("KIỂM TRA SHORTCUT, RÒ RỈ VÀ TÍNH TOÀN VẸN ĐẶC TRƯNG")
    print("="*70)
    
    ds_path = "data/datasense_10sec_processed.parquet"
    nfuq_path = "data/nfuqnids_processed.parquet"
    
    # 1. DataSense
    print("\n--- 1. Kiểm tra DataSense IIoT 2025 (71 đặc trưng) ---")
    feats_ds, (Xtr_ds, ytr_ds, Xva_ds, yva_ds, Xte_ds, yte_ds), cls_ds = load_split(ds_path)
    const_ds = check_constant_features("DataSense", Xtr_ds, feats_ds)
    print(f"Cột hằng (variance=0 trong Train): {const_ds if const_ds else 'Không có (0 cột)'}")
    
    dups_ds, total_ds, pct_ds = check_train_test_duplicates(Xtr_ds, ytr_ds, Xte_ds, yte_ds)
    print(f"Trùng lặp vector đặc trưng Test trong Train: {dups_ds}/{total_ds} hàng ({pct_ds:.2f}%)")
    
    print("\nQuét mô hình 1 đặc trưng đơn lẻ (threshold Macro-F1 >= 0.70):")
    flagged_ds = check_single_features(Xtr_ds, ytr_ds, Xte_ds, yte_ds, feats_ds, cls_ds, threshold=0.70)
    if flagged_ds:
        for f, f1 in flagged_ds:
            print(f"  [CANH BAO] Đặc trưng '{f}': Test Macro-F1 = {f1:.4f}")
    else:
        print("  Không có đặc trưng đơn lẻ nào vượt quá Macro-F1 0.70")
        
    print("\nThử nghiệm loại bỏ nhóm 7 đặc trưng log (log_* ablation):")
    res_abl = check_log_ablation(ds_path)
    print(f"  Đủ 71 đặc trưng: Val Macro-F1 = {res_abl['all_71'][0]:.4f} | Test Macro-F1 = {res_abl['all_71'][1]:.4f}")
    print(f"  Bỏ 7 đặc trưng log (còn 64 đặc trưng mạng): Val Macro-F1 = {res_abl['no_log_64'][0]:.4f} | Test Macro-F1 = {res_abl['no_log_64'][1]:.4f}")
    print(f"  Chênh lệch (Drop loss): Delta Val = {res_abl['diff_val']:+.4f} | Delta Test = {res_abl['diff_test']:+.4f}")

    # 2. NF-UQ-NIDS-v2
    print("\n--- 2. Kiểm tra NF-UQ-NIDS-v2 (39 đặc trưng) ---")
    feats_nf, (Xtr_nf, ytr_nf, Xva_nf, yva_nf, Xte_nf, yte_nf), cls_nf = load_split(nfuq_path)
    const_nf = check_constant_features("NF-UQ", Xtr_nf, feats_nf)
    print(f"Cột hằng (variance=0 trong Train): {const_nf if const_nf else 'Không có (0 cột)'}")
    
    dups_nf, total_nf, pct_nf = check_train_test_duplicates(Xtr_nf, ytr_nf, Xte_nf, yte_nf)
    print(f"Trùng lặp vector đặc trưng Test trong Train: {dups_nf}/{total_nf} hàng ({pct_nf:.2f}%)")
    
    print("\nQuét mô hình 1 đặc trưng đơn lẻ trên NF-UQ (threshold Macro-F1 >= 0.70):")
    flagged_nf = check_single_features(Xtr_nf, ytr_nf, Xte_nf, yte_nf, feats_nf, cls_nf, threshold=0.70)
    if flagged_nf:
        for f, f1 in flagged_nf:
            print(f"  [CANH BAO] Đặc trưng '{f}': Test Macro-F1 = {f1:.4f}")
    else:
        print("  Không có đặc trưng đơn lẻ nào vượt quá Macro-F1 0.70")
        
    print("\n" + "="*70)
    print("HOÀN THÀNH KIỂM TRA SHORTCUT & RÒ RỈ")
    print("="*70)

if __name__ == "__main__":
    main()
