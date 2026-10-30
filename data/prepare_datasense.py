"""
Gop attack_samples_<N>sec.csv + benign_samples_<N>sec.csv cua DataSense IIoT 2025 -> 1 file Parquet.

- Chi doc cac cot SO (bo cot danh sach dang chuoi: IP/MAC/port/protocol, log_data-types)
  va bo cot dinh danh/thoi gian de tranh ro ri (device_name, device_mac, timestamp, label_full...).
- Chon cot nhan: label1 (nhi phan), label2 (benign + 7 nhom tan cong), label3/label4 (loai tan cong chi tiet).
- Chia train/val/test THEO THOI GIAN trong tung kich ban (label_full): 60% dau -> train,
  20% tiep -> val, 20% cuoi -> test. Cach nay tranh viec cac cua so lien ke nhau roi vao ca train lan test.
- Cot meta_* chi dung de chia/kiem tra, nsga2_fs.py se tu bo khoi tap dac trung.

Vi du:
  python prepare_datasense.py --root /mnt/.../all_attack_benign_samples --window 10 \
      --label label2 --out /mnt/.../dacn/data/datasense_10s_label2.parquet
"""
import argparse
import glob
import os
import re

import numpy as np
import pandas as pd

META = ["device_name", "device_mac", "label_full", "label1", "label2", "label3", "label4",
        "timestamp", "timestamp_start", "timestamp_end"]
# cot dang danh sach (chuoi) -> bo, vi da co cot *_count tuong ung
LIST_RE = re.compile(r"^(network_(ips|macs|ports|protocols)_(all|dst|src)|log_data-types)$")


def find(root, name):
    hits = [h for h in glob.glob(os.path.join(root, "**", name), recursive=True)
            if not h.endswith(".xz")]
    if not hits:
        raise SystemExit(f"Khong tim thay {name} trong {root}")
    return hits[0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="thu muc chua attack_samples_*sec.csv va benign_samples_*sec.csv")
    ap.add_argument("--window", type=int, default=10, help="cua so thoi gian (giay): 1..10")
    ap.add_argument("--label", default="label2", choices=["label1", "label2", "label3", "label4", "label_full"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--train", type=float, default=0.6)
    ap.add_argument("--val", type=float, default=0.2)
    args = ap.parse_args()

    paths = [find(args.root, f"attack_samples_{args.window}sec.csv"),
             find(args.root, f"benign_samples_{args.window}sec.csv")]
    print("Doc:", *paths, sep="\n  ")

    header = pd.read_csv(paths[0], nrows=0).columns.tolist()
    feats = [c for c in header if c not in META and not LIST_RE.match(c)]
    print(f"So cot dac trung so giu lai: {len(feats)}")
    keep = list(dict.fromkeys([args.label, "label_full", "timestamp_start"] + feats))
    dtypes = {c: "float32" for c in feats}

    df = pd.concat([pd.read_csv(p, usecols=keep, dtype=dtypes) for p in paths], ignore_index=True)

    X = df[feats].replace([np.inf, -np.inf], np.nan).fillna(0).astype("float32")
    out = X.copy()
    out["label"] = df[args.label].astype(str).values
    out["meta_scenario"] = df["label_full"].astype(str).values
    out["meta_time"] = pd.to_datetime(df["timestamp_start"], utc=True, errors="coerce")

    # chia theo thoi gian trong tung kich ban
    out["meta_split"] = "train"
    small = []
    for scen, g in out.groupby("meta_scenario"):
        g = g.sort_values("meta_time")
        n = len(g)
        if n < 5:
            small.append((scen, n))
            continue
        pos = np.arange(n) / n
        s = np.where(pos < args.train, "train", np.where(pos < args.train + args.val, "val", "test"))
        out.loc[g.index, "meta_split"] = s
    if small:
        print("CANH BAO: kich ban qua it mau (<5), chi dua vao train:", small)

    out["meta_time"] = out["meta_time"].astype(str)
    out.to_parquet(args.out, index=False)

    print(f"\nDa luu {args.out}: {out.shape[0]:,} dong, {len(feats)} dac trung")
    ct = pd.crosstab(out["label"], out["meta_split"])
    ct["percent"] = (100 * ct.sum(axis=1) / ct.sum().sum()).round(2)
    print(ct.to_string())
    missing = [l for l in ct.index if ct.loc[l].get("val", 0) == 0 or ct.loc[l].get("test", 0) == 0]
    if missing:
        print("\nCANH BAO: cac lop khong co mau o val hoac test:", missing)


if __name__ == "__main__":
    main()
