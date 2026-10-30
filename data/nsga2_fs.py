"""
NSGA-II chon dac trung da muc tieu cho IDS (Nhom 9).
3 muc tieu (deu minimize):
  f1 = 1 - Macro-F1 (tren tap validation, mau so labels co dinh)
  f2 = so dac trung chon / tong so dac trung
  f3 = thoi gian suy luan trung vi (giay) tren N_TIME=2000 dong validation ngau nhien co dinh (lap 3 lan, n_jobs=1)
"""
import argparse
import json
import os
import pickle
import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from pymoo.operators.crossover.pntx import TwoPointCrossover
from pymoo.operators.mutation.bitflip import BitflipMutation
from pymoo.operators.sampling.rnd import BinaryRandomSampling
from pymoo.util.nds.non_dominated_sorting import NonDominatedSorting

from common import (
    load_split,
    make_model,
    measure_infer_time,
    calc_metrics,
    evaluate_solution,
    subsample,
)

N_TIME_LOOP = 2000   # Theo de cuong: f3 trong vong lap NSGA-II do tren 2.000 mau
N_REPEAT_LOOP = 3    # Lap 3 lan lay trung vi trong vong lap NSGA-II


class FSProblem(ElementwiseProblem):
    def __init__(self, Xtr, ytr, Xva, yva, classes, cache_path=None, seed=0):
        super().__init__(n_var=Xtr.shape[1], n_obj=3, xtype=bool)
        self.Xtr, self.ytr, self.Xva, self.yva = Xtr, ytr, Xva, yva
        self.classes = classes
        self.seed = seed

        # Lay mau ngau nhien 2.000 dong co dinh tren Val de do thoi gian (tranh thien lech kich ban do chia thoi gian)
        rng = np.random.default_rng(0)
        idx_time = rng.choice(len(Xva), min(N_TIME_LOOP, len(Xva)), replace=False)
        self.Xva_time = np.ascontiguousarray(Xva[idx_time], dtype=np.float32)

        # Khoi phuc bo nho dem tu dia neu co de tranh tinh lai khi resume
        self.cache_path = cache_path
        self.cache = {}
        if cache_path and os.path.exists(cache_path):
            try:
                with open(cache_path, "rb") as f:
                    self.cache = pickle.load(f)
                print(f"  [Cache] Da nạp {len(self.cache)} tap dac trung tu dia ({cache_path})")
            except Exception as e:
                print(f"  [Cache] Khong doc duoc cache: {e}, khoi tao rong.")
                self.cache = {}

    def _evaluate(self, x, out, *args, **kwargs):
        mask = np.asarray(x, dtype=bool)
        if mask.sum() == 0:
            out["F"] = [1.0, 1.0, 1.0]  # phat to hop rong
            return
        key = mask.tobytes()
        if key in self.cache:
            out["F"] = self.cache[key]
            return

        m = make_model(60, lr=0.08, n_jobs=2, seed=self.seed)
        m.fit(self.Xtr[:, mask], self.ytr)
        t_med = measure_infer_time(m, self.Xva_time[:, mask], repeats=N_REPEAT_LOOP)
        pred_full = m.predict(self.Xva[:, mask], n_jobs=1)
        f1, _ = calc_metrics(self.yva, pred_full, self.classes)

        F = [1.0 - f1, float(mask.sum() / mask.size), t_med]
        self.cache[key] = F
        out["F"] = F

    def save_cache(self):
        if self.cache_path:
            with open(self.cache_path, "wb") as f:
                pickle.dump(self.cache, f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--label", default="Attack")
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--pop", type=int, default=24)
    ap.add_argument("--gen", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--n_fit", type=int, default=40000, help="so dong train cho fitness")
    ap.add_argument("--trees", type=int, default=150, help="so cay co dinh khi danh gia cuoi")
    ap.add_argument("--delta", type=float, default=0.01, help="nguong sut giam Macro-F1 cho phep tren val")
    args = ap.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    feats, data, classes = load_split(args.data, args.label)
    Xtr, ytr, Xva, yva, Xte, yte = data

    if len(Xtr) > args.n_fit:
        Xfit, yfit = subsample(Xtr, ytr, args.n_fit, args.seed)
    else:
        Xfit, yfit = Xtr, ytr
    Xva_s, yva_s = Xva[:20000], yva[:20000]

    state_path = os.path.join(args.outdir, "state.json")
    pop_path = os.path.join(args.outdir, "pop.npy")
    cache_path = os.path.join(args.outdir, "cache.pkl")
    pareto_x_path = os.path.join(args.outdir, "pareto_X.npy")
    pareto_f_path = os.path.join(args.outdir, "pareto_F.npy")

    problem = FSProblem(Xfit, yfit, Xva_s, yva_s, classes, cache_path=cache_path, seed=args.seed)

    done = 0
    sampling = BinaryRandomSampling()
    if os.path.exists(state_path) and os.path.exists(pop_path):
        try:
            with open(state_path, "r") as f:
                done = json.load(f)["gen"]
            sampling = np.load(pop_path)
            print(f"Tiep tuc tu the he {done} voi quan the nap tu {pop_path}")
        except Exception as e:
            print(f"Canh bao checkpoint: {e}, khoi tao quan the ngau nhien.")
            done = 0

    remaining = args.gen - done
    if remaining <= 0:
        print(f"Da chay du {done}/{args.gen} the he NSGA-II. Bo qua tien hoa, tien hanh danh gia nghiem.")
    else:
        algo = NSGA2(
            pop_size=args.pop,
            sampling=sampling,
            crossover=TwoPointCrossover(),
            mutation=BitflipMutation(),
            eliminate_duplicates=True,
        )
        algo.setup(problem, termination=("n_gen", remaining), seed=args.seed, verbose=False)
        while algo.has_next():
            algo.next()
            done += 1
            np.save(pop_path, algo.pop.get("X"))
            with open(state_path, "w") as f:
                json.dump({"gen": done}, f)
            problem.save_cache()
            best = algo.pop.get("F")[:, 0].min()
            print(f"gen {done}/{args.gen} | best Val Macro-F1 ~ {1.0 - best:.4f} | cache {len(problem.cache)}")

        res = algo.result()
        np.save(pareto_x_path, res.X)
        np.save(pareto_f_path, res.F)

    # Khoi phuc Pareto neu thieu file nhung co pop.npy
    if not os.path.exists(pareto_x_path) and os.path.exists(pop_path):
        pop_X = np.load(pop_path)
        pop_F = []
        for ind in pop_X:
            out_eval = {}
            problem._evaluate(ind, out_eval)
            pop_F.append(out_eval["F"])
        pop_F = np.array(pop_F)
        nds = NonDominatedSorting().do(pop_F, only_non_dominated_front=True)
        Xp = pop_X[nds]
        Fp = pop_F[nds]
        np.save(pareto_x_path, Xp)
        np.save(pareto_f_path, Fp)
        print(f"Da trich xuat va luu {len(Xp)} nghiem Pareto tu pop.npy")
    else:
        Xp = np.load(pareto_x_path)

    if Xp.ndim == 1:
        Xp = Xp.reshape(1, -1)
    Xp = Xp.astype(bool)

    # Danh gia cuoi cung: Dung chung evaluate_solution voi so cay co dinh (150 cay)
    print(f"\n--- Danh gia nghiem Pareto voi {args.trees} cay co dinh ---")
    candidates = [("baseline_all", np.ones(len(feats), dtype=bool))]
    candidates += [(f"pareto_{i}", m) for i, m in enumerate(Xp)]

    rows = []
    for name, mask in candidates:
        if mask.sum() == 0:
            continue
        row, _ = evaluate_solution(
            mask, data, classes,
            trees=args.trees, seed=args.seed,
            timing=True, repeats=5
        )
        row["solution"] = name
        row["selected"] = ""
        row["features"] = ";".join(np.array(feats)[mask])
        rows.append(row)

    out = pd.DataFrame(rows)
    base_val_f1 = out.loc[out["solution"] == "baseline_all", "val_macro_f1"].values[0]

    pareto_df = out[out["solution"] != "baseline_all"].copy()
    valid_df = pareto_df[pareto_df["val_macro_f1"] >= (base_val_f1 - args.delta)]
    if len(valid_df) > 0:
        best_idx = valid_df.sort_values(["n_features", "val_infer_s"]).index[0]
        out.loc[best_idx, "selected"] = f"chosen_delta({args.delta})"

    if len(pareto_df) > 1:
        f1_loss = 1.0 - pareto_df["val_macro_f1"].to_numpy()
        f2_norm = pareto_df["n_features"].to_numpy() / len(feats)
        f3_raw = pareto_df["val_infer_s"].to_numpy()
        M = np.vstack([f1_loss, f2_norm, f3_raw]).T
        ptp = np.ptp(M, axis=0)
        ptp[ptp == 0] = 1.0
        M_norm = (M - M.min(axis=0)) / ptp
        knee_idx = pareto_df.index[np.argmin(np.linalg.norm(M_norm, axis=1))]
        cur_tag = out.loc[knee_idx, "selected"]
        out.loc[knee_idx, "selected"] = (cur_tag + ";knee_balanced").strip(";")

    out = out.sort_values("n_features")
    out.to_csv(os.path.join(args.outdir, "final_eval.csv"), index=False)
    print(out.drop(columns="features").to_string(index=False))


if __name__ == "__main__":
    main()
