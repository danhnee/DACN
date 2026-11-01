"""
Baseline chon dac trung de so sanh voi NSGA-II (Nhom 9) - cung k, cung quy trinh danh gia.

Phuong phap:
  all          : toan bo dac trung
  random       : chon ngau nhien k dac trung (lap n_random lan moi k)
  mi           : top-k theo Mutual Information (tren tap con train)
  lgbm_imp     : top-k theo do quan trong (gain) cua LightGBM
  boruta_lite  : Boruta rut gon (dac trung bong + dem so lan thang), xep hang theo so lan thang roi do quan trong
  nsga2        : (tuy chon, --pareto_dir) danh gia lai cac nghiem Pareto cua NSGA-II DUNG CUNG quy trinh

Quy trinh danh gia chung: huan luyen LightGBM voi SO CAY CO DINH (150 cay, khong early stopping) tren toan bo train,
danh gia tren val va test thong qua ham evaluate_solution tu common.py.
"""
import argparse
import os
import time
import numpy as np
import pandas as pd
from scipy.stats import binomtest
from sklearn.feature_selection import mutual_info_classif

from common import (
    load_split,
    make_model,
    measure_infer_time,
    calc_metrics,
    evaluate_solution,
    subsample,
)


# ---------------- cac phuong phap xep hang dac trung ----------------
def rank_mi(Xf, yf, seed):
    mi = mutual_info_classif(Xf, yf, random_state=seed)
    return np.argsort(-mi), mi


def rank_lgbm(Xf, yf, seed):
    m = make_model(150, seed=seed)
    m.fit(Xf, yf)
    imp = m.booster_.feature_importance(importance_type="gain")
    return np.argsort(-imp), imp


def rank_boruta_lite(Xf, yf, seed, n_iter=20, n_rows=10000):
    """
    Boruta rut gon: moi vong tao ban sao xao tron tung cot (dac trung bong), huan luyen LightGBM tren
    [that | bong]; dac trung that 'thang' neu gain > gain lon nhat cua dac trung bong. Xep hang theo so lan thang.
    """
    rng = np.random.default_rng(seed)
    Xs, ys = subsample(Xf, yf, n_rows, seed)
    d = Xs.shape[1]
    hits = np.zeros(d)
    imps = np.zeros(d)
    for it in range(n_iter):
        shadow = np.empty_like(Xs)
        for j in range(d):
            shadow[:, j] = rng.permutation(Xs[:, j])
        m = make_model(50, seed=seed + it)
        m.fit(np.hstack([Xs, shadow]), ys)
        g = m.booster_.feature_importance(importance_type="gain")
        real, sh = g[:d], g[d:]
        hits += real > sh.max()
        imps += real
    order = np.lexsort((-imps, -hits))  # uu tien so lan thang, hoa thi xet gain
    confirmed = sum(binomtest(int(h), n_iter, 0.5, alternative="greater").pvalue < 0.01 for h in hits)
    print(f"  Boruta rut gon: {confirmed}/{d} dac trung duoc xac nhan (p<0.01)")
    return order, hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--label", default=None, help="cot nhan (None de tu nhan dien Attack/label)")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--ks", type=int, nargs="*", default=None, help="cac gia tri k; mac dinh: luoi + kich thuoc Pareto")
    ap.add_argument("--pareto_dir", default=None, help="thu muc ket qua NSGA-II (co pareto_X.npy)")
    ap.add_argument("--n_random", type=int, default=20, help="so tap ngau nhien moi k")
    ap.add_argument("--trees", type=int, default=150, help="so cay co dinh khi danh gia")
    ap.add_argument("--n_fit", type=int, default=40000, help="so dong train de xep hang dac trung")
    ap.add_argument("--no_boruta", action="store_true")
    ap.add_argument("--time_random", action="store_true", help="do ca thoi gian suy luan cho tap ngau nhien (cham)")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    feats, data, classes = load_split(args.data, args.label)
    Xtr, ytr = data[0], data[1]
    d = len(feats)
    feats_arr = np.array(feats)
    Xfit, yfit = subsample(Xtr, ytr, args.n_fit, args.seed)

    pareto = None
    if args.pareto_dir:
        pareto = np.load(os.path.join(args.pareto_dir, "pareto_X.npy"))
        pareto = pareto.reshape(1, -1) if pareto.ndim == 1 else pareto
        pareto = pareto.astype(bool)

    if args.ks:
        ks = set(args.ks)
    else:
        ks = {5, 10, 15, 20, 25, 30, 40, 50}
        if pareto is not None:
            ks |= set(int(m.sum()) for m in pareto)
    ks = sorted(k for k in ks if 0 < k < d)
    print("k can so sanh:", ks)

    rows = []
    csv_path = os.path.join(args.outdir, "baselines_eval.csv")

    def add(method, k, seed_tag, mask, timing, extra=None):
        t0 = time.perf_counter()
        r, _ = evaluate_solution(mask, data, classes, trees=args.trees, seed=args.seed, timing=timing, repeats=5)
        r.update({
            "method": method,
            "k": k,
            "run": seed_tag,
            "features": ";".join(feats_arr[mask])
        })
        if extra:
            r.update(extra)
        rows.append(r)
        print(f"  {method:12s} k={k:<3d} run={seed_tag} test_F1={r['test_macro_f1']:.4f} ({time.perf_counter() - t0:.0f}s)")

    def save():
        pd.DataFrame(rows).to_csv(csv_path, index=False)

    # 1) toan bo dac trung
    print("== all")
    add("all", d, 0, np.ones(d, dtype=bool), True)
    save()

    # 2) cac phuong phap xep hang
    rankers = [("mi", rank_mi), ("lgbm_imp", rank_lgbm)]
    if not args.no_boruta:
        rankers.append(("boruta_lite", rank_boruta_lite))
    for name, fn in rankers:
        print(f"== {name}")
        order, _ = fn(Xfit, yfit, args.seed)
        for k in ks:
            mask = np.zeros(d, dtype=bool)
            mask[order[:k]] = True
            add(name, k, 0, mask, True)
        save()

    # 3) ngau nhien cung k (doc lap danh sach k bang default_rng([seed, k, r]))
    print("== random")
    for k in ks:
        for r in range(args.n_random):
            rng_kr = np.random.default_rng([args.seed, k, r])
            mask = np.zeros(d, dtype=bool)
            mask[rng_kr.choice(d, k, replace=False)] = True
            add("random", k, r, mask, args.time_random)
        save()

    # 4) danh gia lai nghiem NSGA-II cung quy trinh
    if pareto is not None:
        print("== nsga2 (danh gia lai voi so cay co dinh)")
        for i, mask in enumerate(pareto):
            if mask.sum() == 0:
                continue
            add("nsga2", int(mask.sum()), i, mask, True)
        save()

    # tom tat
    df = pd.DataFrame(rows)
    g = df.groupby(["method", "k"]).agg(
        runs=("test_macro_f1", "size"),
        val_f1=("val_macro_f1", "mean"),
        test_f1=("test_macro_f1", "mean"),
        test_f1_std=("test_macro_f1", "std"),
        test_mcc=("test_mcc", "mean"),
        test_f1_max=("test_macro_f1", "max"),
        test_infer_s=("test_infer_s", "mean") if "test_infer_s" in df else ("test_macro_f1", "size"),
    ).reset_index()
    g.to_csv(os.path.join(args.outdir, "baselines_summary.csv"), index=False)
    print("\n== Test Macro-F1 theo phuong phap va k (random: trung binh cua cac lan chay)")
    print(df.pivot_table(index="k", columns="method", values="test_macro_f1", aggfunc="mean").round(4).to_string())
    print(f"\nDa luu: {csv_path}")


if __name__ == "__main__":
    main()
