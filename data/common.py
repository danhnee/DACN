"""
Module dung chung cho de tai Chon dac trung da muc tieu IDS (Nhom 9).
Chua cac ham tien ich: doc du lieu, kiem tra do toan ven dac trung, tao mo hinh LightGBM,
tinh toan do do chuan hoa (Macro-F1 voi labels co dinh, MCC) va danh gia nghiem co dinh so cay.
"""
import time
import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, matthews_corrcoef
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

FORBIDDEN_KEYWORDS = ["device_name", "device_mac", "timestamp", "label1", "label3", "label4", "label_full"]


def load_split(path, label="Attack"):
    """
    Doc du lieu tu file Parquet, kiem tra so chieu dac trung va chia train/val/test.
    Tra ve:
      feats: danh sach ten dac trung hop le
      data: tuple (Xtr, ytr, Xva, yva, Xte, yte) kieu float32
      classes: mang chua tat ca cac lop duy nhat (dung de co dinh mau so Macro-F1)
    """
    df = pd.read_parquet(path)
    feats = [c for c in df.columns if c != label and not c.startswith("meta_")]
    d = len(feats)

    # 1. Kiem tra tinh toan ven so chieu theo de cuong
    assert d in (71, 39), f"Loi du lieu: So dac trung ({d}) khong khop de cuong (phai la 71 cho DataSense hoac 39 cho NF-UQ)"

    # 2. Kiem tra cac cot cam de tranh ro ri thong tin
    leaked = [c for c in feats if any(k in c.lower() for k in FORBIDDEN_KEYWORDS)]
    assert not leaked, f"Canh bao ro ri: Phat hien cac cot khong hop le trong tap dac trung: {leaked}"

    le = LabelEncoder()
    y = le.fit_transform(df[label])
    classes = np.arange(len(le.classes_))
    X = np.ascontiguousarray(df[feats].to_numpy(dtype=np.float32))

    if "meta_split" in df.columns:
        sp = df["meta_split"].to_numpy()
        Xtr, ytr = X[sp == "train"], y[sp == "train"]
        Xva, yva = X[sp == "val"], y[sp == "val"]
        Xte, yte = X[sp == "test"], y[sp == "test"]
        print(f"Chia theo meta_split (thoi gian): train={len(Xtr)}, val={len(Xva)}, test={len(Xte)} | d={d}")
    else:
        Xtr, Xtmp, ytr, ytmp = train_test_split(X, y, test_size=0.4, stratify=y, random_state=0)
        Xva, Xte, yva, yte = train_test_split(Xtmp, ytmp, test_size=0.5, stratify=ytmp, random_state=0)
        print(f"Chia phan tang 60/20/20: train={len(Xtr)}, val={len(Xva)}, test={len(Xte)} | d={d}")

    # Kiem tra so lop xuat hien trong tung tap
    print(f"So lop duy nhat: train={len(np.unique(ytr))}/{len(classes)}, val={len(np.unique(yva))}/{len(classes)}, test={len(np.unique(yte))}/{len(classes)}")

    return feats, (Xtr, ytr, Xva, yva, Xte, yte), classes


def make_model(n_estimators=150, lr=0.08, n_jobs=2, seed=0):
    """
    Khoi tao mo hinh LightGBM Classifier chuan theo cau hinh de tai.
    """
    return lgb.LGBMClassifier(
        n_estimators=n_estimators,
        learning_rate=lr,
        num_leaves=31,
        max_bin=63,
        max_delta_step=1.0,      # Chong bung no gradient tren lop hiem
        min_child_weight=1e-2,   # On dinh Hessian cho multiclass mat can bang
        n_jobs=n_jobs,
        verbose=-1,
        random_state=seed,
    )


def measure_infer_time(model, X_sub, repeats=3):
    """
    Do thoi gian suy luan trung vi tren mang lien tuc, co buoc warm-up.
    """
    X_c = np.ascontiguousarray(X_sub, dtype=np.float32)
    _ = model.predict(X_c[:min(200, len(X_c))], n_jobs=1)  # warm-up nhe
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        _ = model.predict(X_c, n_jobs=1)
        ts.append(time.perf_counter() - t0)
    return float(np.median(ts))


def calc_metrics(y_true, y_pred, classes):
    """
    Tinh Macro-F1 va MCC voi mau so co dinh (labels=classes, zero_division=0)
    de tranh bien dong mau so khi tap val/test thieu lop.
    """
    f1 = float(f1_score(y_true, y_pred, labels=classes, average="macro", zero_division=0))
    mcc = float(matthews_corrcoef(y_true, y_pred))
    return f1, mcc


def evaluate_solution(mask, data, classes, trees=150, seed=0, timing=True, repeats=5):
    """
    Quy trinh danh gia chung voi SO CAY CO DINH (khong early stopping)
    bao dam su dong nhat tuyet doi giua NSGA-II va Baseline.
    """
    Xtr, ytr, Xva, yva, Xte, yte = data
    m = make_model(trees, seed=seed)
    m.fit(Xtr[:, mask], ytr)

    val_pred = m.predict(Xva[:, mask], n_jobs=1)
    val_f1, val_mcc = calc_metrics(yva, val_pred, classes)

    test_pred = m.predict(Xte[:, mask], n_jobs=1)
    test_f1, test_mcc = calc_metrics(yte, test_pred, classes)

    n_feats = int(mask.sum())
    total_feats = int(mask.size)
    row = {
        "n_features": n_feats,
        "reduction_%": round(100.0 * (1.0 - n_feats / total_feats), 1),
        "val_macro_f1": val_f1,
        "val_mcc": val_mcc,
        "test_macro_f1": test_f1,
        "test_mcc": test_mcc,
        "n_trees": trees,
    }
    if timing:
        # Lay 5.000 mau dau tien cua Val va Test de do thoi gian suy luan danh gia cuoi
        Xva_5k = np.ascontiguousarray(Xva[:5000][:, mask], dtype=np.float32)
        Xte_5k = np.ascontiguousarray(Xte[:5000][:, mask], dtype=np.float32)
        row["val_infer_s"] = measure_infer_time(m, Xva_5k, repeats=repeats)
        row["test_infer_s"] = measure_infer_time(m, Xte_5k, repeats=repeats)
    return row, m


def subsample(X, y, n, seed):
    """
    Lay mau phan tang n dong tu tap du lieu.
    """
    if len(X) <= n:
        return X, y
    idx, _ = train_test_split(np.arange(len(X)), train_size=n, stratify=y, random_state=seed)
    return X[idx], y[idx]
