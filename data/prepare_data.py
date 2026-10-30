"""
Lay mau phan tang tu CSV rat lon (vd NF-UQ-NIDS-v2) -> Parquet float32.
Doc theo chunk nen it ton RAM. Hai luot:
  luot 1: dem so dong moi lop (chi doc cot nhan)
  luot 2: moi lop giu toi da `cap` dong (lop hiem giu het)

Vi du:
  python prepare_data.py --csv /mnt/.../NF-UQ-NIDS-v2.csv \
      --out /mnt/.../dacn/data/nfuq_sample.parquet --label Attack --cap 40000
"""
import argparse
import numpy as np
import pandas as pd

DEFAULT_DROP = ["IPV4_SRC_ADDR", "IPV4_DST_ADDR", "L4_SRC_PORT", "L4_DST_PORT",
                "Label", "Dataset", "FLOW_START_MILLISECONDS", "FLOW_END_MILLISECONDS"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", default="Attack", help="cot nhan da lop")
    ap.add_argument("--cap", type=int, default=40000, help="so dong toi da moi lop")
    ap.add_argument("--chunksize", type=int, default=500_000)
    ap.add_argument("--drop", nargs="*", default=DEFAULT_DROP,
                    help="cot bo (dinh danh, nhan nhi phan...). Cot khong ton tai se bi bo qua")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)

    # Luot 1: dem lop
    counts = {}
    for ch in pd.read_csv(args.csv, usecols=[args.label], chunksize=args.chunksize):
        for k, v in ch[args.label].value_counts().items():
            counts[k] = counts.get(k, 0) + int(v)
    print("So dong moi lop:", counts)
    prob = {k: min(1.0, args.cap / v) for k, v in counts.items()}

    # Luot 2: lay mau
    parts = []
    for i, ch in enumerate(pd.read_csv(args.csv, chunksize=args.chunksize)):
        p = ch[args.label].map(prob).to_numpy()
        keep = rng.random(len(ch)) < p
        parts.append(ch[keep])
        print(f"chunk {i}: giu {keep.sum()} / {len(ch)}")

    df = pd.concat(parts, ignore_index=True)
    drop = [c for c in args.drop if c in df.columns and c != args.label]
    df = df.drop(columns=drop)

    y = df[args.label].astype(str)
    X = df.drop(columns=[args.label])
    X = X.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan)
    X = X.fillna(0).astype("float32")
    X[args.label] = y.values

    X.to_parquet(args.out, index=False)
    print("Da luu:", args.out, X.shape)
    print(X[args.label].value_counts())


if __name__ == "__main__":
    main()
