# THƯ MỤC KẾT QUẢ THỰC NGHIỆM (`results/`)

Thư mục này lưu trữ toàn bộ các tệp kết quả thực nghiệm, nhật ký chạy máy (logs), checkpoint trạng thái tiến hóa và các mô hình Pareto thu được trong đề tài:
> **"Lựa chọn đặc trưng đa mục tiêu bằng NSGA-II cho hệ thống phát hiện xâm nhập trên thiết bị tài nguyên hạn chế"**  
> **Nhóm thực hiện:** Nhóm 9 (Nguyễn Thành Danh, Vũ Đức Nam, Nguyễn Minh Nhật)  
> **GVHD:** ThS. Nguyễn Trọng Minh Hồng Phước  
> **Cập nhật:** Chuẩn hóa toàn diện v2 (Mở rộng thực nghiệm đa seed: Seed 42, Seed 43, Seed 44...)

---

## 1. CÂY CẤU TRÚC THƯ MỤC THỰC NGHIỆM

```text
results/
├── README.md                                # [Tệp này] Tài liệu mô tả cấu trúc và tổng hợp số liệu
│
├── [THỰC NGHIỆM CHUẨN HÓA V2 - DATASENSE IIOT 2025]
├── v2_ds_s42/ ~ s44/                        # NSGA-II v2 trên DataSense (24 pop, 20 gen, 480 evals)
│   ├── final_eval.csv                       # Đánh giá 24 nghiệm Pareto trên Val & Test (150 cây cố định)
│   ├── pareto_F.npy                         # Ma trận 3 mục tiêu [1-F1, |S|/d, t_pred] của nghiệm không trội
│   ├── pareto_X.npy                         # Mặt nạ nhị phân boolean (chọn/bỏ) tương ứng của các nghiệm Pareto
│   ├── pop.npy                              # Quần thể cá thể ở thế hệ 20
│   ├── state.json                           # Checkpoint thế hệ {"gen": 20}
│   └── cache.pkl                            # Bộ nhớ đệm băm cấu hình config_meta
├── v2_base_datasense_s42/ ~ s44/            # 5 Baseline đối chứng v2 trên DataSense (10 mức k, 20 runs/k)
│   ├── baselines_eval.csv                   # Chi tiết từng lượt chạy đơn lẻ (gồm 20 runs random/k)
│   └── baselines_summary.csv                # Bảng tổng hợp theo phương pháp và số đặc trưng k
│
├── [THỰC NGHIỆM CHUẨN HÓA V2 - NF-UQ-NIDS-V2]
├── v2_nfuq_s42/ ~ s44/                      # NSGA-II v2 trên NF-UQ (167k mẫu, 21 lớp, 39 đặc trưng)
│   ├── final_eval.csv                       # Đánh giá chi tiết nghiệm Pareto trên Val & Test
│   ├── pareto_F.npy, pareto_X.npy           # Nghiệm không trội & mặt nạ nhị phân
│   ├── pop.npy, state.json, cache.pkl       # Checkpoint tiến hóa và bộ nhớ đệm
├── v2_base_nfuq_s42/ ~ s44/                 # 5 Baseline đối chứng v2 trên NF-UQ (7 mức k, 20 runs/k)
│   ├── baselines_eval.csv, baselines_summary.csv
│
├── [ĐO HIỆU NĂNG TRÊN THIẾT BỊ BIÊN GIẢ LẬP E1 / E2]
├── edge_benchmark_summary.csv               # Kết quả đo latency (IQR) và RSS RAM trên E1 (1 CPU, 512MB RAM)
├── edge_benchmark_summary_E2.csv            # Kết quả đo latency và RSS RAM trên E2 (2 CPU, 1GB RAM)
│
└── [LƯU TRỮ LỊCH SỬ V1 (SMOKE TEST & CHẠY SƠ BỘ TRƯỚC VÁ MÃ NGUỒN)]
    ├── ds_s42/, base_ds_s42/, base_nfuq_s42/
    ├── test_datasense_10sec/, test_nfuqnids/
    └── base_datasense_s42/, base_ds_quick/
```

---

## 2. QUY CHUẨN THỰC NGHIỆM V2 (CHUẨN HÓA A.1 – A.10)

Để bảo đảm tính liêm chính và nhất quán khoa học 100%, toàn bộ kết quả trong các thư mục `v2_...` tuân thủ nghiêm ngặt 10 nguyên tắc sau:
1. **Mục tiêu $f_3$ (Thời gian suy luận):** Đo trên $2.000$ mẫu Validation ngẫu nhiên cố định (lấy bằng `rng.choice(len(Xva), 2000, replace=False)`) thay vì cắt lát tuần tự, lặp 3 lần lấy trung vị ($n\_jobs=1$).
2. **Bảo vệ Cache bằng băm cấu hình (`config_meta`):** Checkpoint `cache.pkl` lưu kèm siêu dữ liệu cấu hình ($n\_var, n\_tr, n\_va, classes, seed, trees$), nếu khác biệt sẽ tự động tạo mới, ngăn chặn tuyệt đối dùng lẫn cache.
3. **Cơ chế khôi phục thế hệ chính xác:** Sửa lỗi lệch số vòng lặp khi resume trong `pymoo` (`remaining + 1` khi khôi phục checkpoint).
4. **Độc lập hạt giống ngẫu nhiên cho Baseline Random:** Khởi tạo `default_rng([seed, k, r])` độc lập hoàn toàn giữa các giá trị $k$ và lượt lặp $r$, loại bỏ hiện tượng tập con $k$ lớn bị phụ thuộc tập con $k$ nhỏ.
5. **Số lượt lặp Random:** Tăng lên **20 lượt chạy ngẫu nhiên độc lập** cho mỗi mức $k$ để báo cáo kỳ vọng và độ lệch chuẩn tin cậy.
6. **Xác định nghiệm Knee cân bằng:** Tính khoảng cách Euclid tới điểm lý tưởng $(0, 0)$ trên không gian chuẩn hóa $(f_1, f_2)$ với $f_1 = 1 - \text{Val F1} \in [0, 1]$ và $f_2 = |S|/d \in [0, 1]$.
7. **Cố định số cây đánh giá:** Toàn bộ nghiệm Pareto và các Baseline đều được đánh giá bằng LightGBM với **cố định 150 cây** (`n_estimators=150`, không early stopping).
8. **Đồng nhất số mức $k$ so sánh:**
   - **DataSense (71 đặc trưng):** 10 mức $k \in \{5, 10, 15, 20, 25, 30, 35, 40, 50, 60\}$.
   - **NF-UQ-NIDS-v2 (39 đặc trưng):** 7 mức $k \in \{5, 10, 15, 20, 25, 30, 35\}$.
9. **Bảo toàn tập Test:** Chỉ đánh giá tập Test đúng 1 lần cho báo cáo cuối cùng, không tham gia vào bất kỳ khâu chọn lọc đặc trưng hay chọn nghiệm nào.
10. **Tách biệt kết quả:** Toàn bộ kết quả mới lưu tại thư mục `v2_...`, không ghi đè dữ liệu cũ.

---

## 3. TỔNG HỢP SỐ LIỆU ĐA SEED V2 (SEEDS 42, 43, 44)

### 3.1. Dữ liệu DataSense IIoT 2025 (71 đặc trưng, chia thời gian 60/20/20)
*Toàn bộ đặc trưng (`all`, $k=71$): Val Macro-F1 = 0.9700, Test Macro-F1 = **0.9738**, Test MCC = 0.9677.*

| Seed | Nghiệm | Số đặc trưng $k$ | Tỷ lệ giảm | Val Macro-F1 | Test Macro-F1 | Test MCC | Nguồn tệp CSV |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| **s42** | **Nghiệm chọn $\delta = 1\%$** | **17** | **76.1%** | **0.9669** | **0.9700** | **0.9601** | `v2_ds_s42/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 13 | 81.7% | 0.9404 | 0.9501 | 0.9416 | `v2_ds_s42/final_eval.csv` |
| **s43** | **Nghiệm chọn $\delta = 1\%$** | **23** | **67.6%** | **0.9651** | **0.9681** | **0.9619** | `v2_ds_s43/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 18 | 74.6% | 0.9273 | 0.9432 | 0.9300 | `v2_ds_s43/final_eval.csv` |
| **s44** | **Nghiệm chọn $\delta = 1\%$** | **18** | **74.6%** | **0.9630** | **0.9708** | **0.9605** | `v2_ds_s44/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 15 | 78.9% | 0.9274 | 0.9375 | 0.9274 | `v2_ds_s44/final_eval.csv` |
| **Trung bình** | **Nghiệm chọn $\delta = 1\%$** | **19.3 $\pm$ 3.2** | **72.8%** | **0.9650** | **0.9696 $\pm$ 0.0014** | **0.9608** | *(Tổng hợp 3 seed)* |

**So sánh đối chứng với các Baseline trên DataSense (Test Macro-F1 trung bình 3 seed):**
- Tại vùng $k \approx 18 - 20$:
  + **NSGA-II (Nghiệm $\delta$, $k \approx 19$):** **0.9696**
  + **Boruta rút gọn ($k=20$):** 0.9684
  + **LightGBM Gain ($k=20$):** 0.9687
  + **Mutual Information ($k=20$):** 0.9664
  + **Random Selection ($k=20$, 20 runs):** 0.9498 $\pm$ 0.012

---

### 3.2. Dữ liệu NF-UQ-NIDS-v2 (39 đặc trưng NetFlow, phân tầng 60/20/20)
*Toàn bộ đặc trưng (`all`, $k=39$): Val Macro-F1 = 0.8842, Test Macro-F1 = **0.8872**, Test MCC = 0.8921.*

| Seed | Nghiệm | Số đặc trưng $k$ | Tỷ lệ giảm | Val Macro-F1 | Test Macro-F1 | Test MCC | Nguồn tệp CSV |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| **s42** | **Nghiệm chọn $\delta = 1\%$** | **13** | **66.7%** | **0.8767** | **0.8808** | **0.8875** | `v2_nfuq_s42/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 9 | 76.9% | 0.8354 | 0.8396 | 0.8687 | `v2_nfuq_s42/final_eval.csv` |
| **s43** | **Nghiệm chọn $\delta = 1\%$** | **10** | **74.4%** | **0.8745** | **0.8765** | **0.8860** | `v2_nfuq_s43/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 6 | 84.6% | 0.8491 | 0.8543 | 0.8732 | `v2_nfuq_s43/final_eval.csv` |
| **s44** | **Nghiệm chọn $\delta = 1\%$** | **15** | **61.5%** | **0.8756** | **0.8812** | **0.8875** | `v2_nfuq_s44/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 7 | 82.1% | 0.8255 | 0.8314 | 0.8654 | `v2_nfuq_s44/final_eval.csv` |
| **Trung bình** | **Nghiệm chọn $\delta = 1\%$** | **12.7 $\pm$ 2.5** | **67.5%** | **0.8756** | **0.8795 $\pm$ 0.0026** | **0.8870** | *(Tổng hợp 3 seed)* |

**So sánh đối chứng với các Baseline trên NF-UQ (Test Macro-F1 trung bình 3 seed):**
- Tại vùng $k \approx 13 - 15$:
  + **NSGA-II (Nghiệm $\delta$, $k \approx 13$):** **0.8795**
  + **Boruta rút gọn ($k=15$):** 0.8795
  + **LightGBM Gain ($k=15$):** 0.8806
  + **Mutual Information ($k=15$):** 0.8775
  + **Random Selection ($k=15$, 20 runs):** 0.8465 $\pm$ 0.021

---

## 4. TỪ ĐIỂN DỮ LIỆU CÁC CỘT (DATA DICTIONARY)

### 4.1. Cấu trúc tệp `final_eval.csv` (trong thư mục NSGA-II v2)
| Cột | Kiểu | Ý nghĩa |
| :--- | :---: | :--- |
| `solution` | string | Tên định danh nghiệm: `pareto_0`, `pareto_1`, ..., `baseline_all` |
| `n_features` | integer | Số lượng đặc trưng được chọn ($k = |S|$) |
| `reduction_%` | float | Tỷ lệ giảm số chiều: $\frac{d - |S|}{d} \times 100\%$ |
| `val_macro_f1` | float | Điểm Macro-F1 trên tập Validation (mẫu số nhãn cố định) |
| `val_mcc` | float | Điểm Matthews Correlation Coefficient trên tập Validation |
| `val_infer_s` | float | Thời gian suy luận trung vị (giây) trên tập mẫu Validation |
| `test_macro_f1` | float | Điểm Macro-F1 đánh giá trên tập Test độc lập |
| `test_mcc` | float | Điểm MCC trên tập Test độc lập |
| `test_infer_s` | float | Thời gian suy luận (giây) trên toàn bộ tập Test |
| `selected` | string | Đánh dấu nghiệm chọn: `chosen_delta(0.01)` hoặc `knee_balanced` |
| `features` | string | Danh sách tên đặc trưng được chọn (phân cách bằng dấu chấm phẩy `;`) |

### 4.2. Cấu trúc tệp `baselines_summary.csv` (trong thư mục Baseline v2)
| Cột | Kiểu | Ý nghĩa |
| :--- | :---: | :--- |
| `method` | string | Phương pháp: `all`, `boruta_lite`, `lgbm_imp`, `mi`, `random` |
| `k` | integer | Số lượng đặc trưng được chọn |
| `runs` | integer | Số lượt chạy độc lập (20 lượt với `random`, 1 lượt với các phương pháp khác) |
| `val_f1` | float | Điểm Macro-F1 trung bình trên tập Validation |
| `test_f1` | float | Điểm Macro-F1 trung bình trên tập Test độc lập |
| `test_f1_std` | float | Độ lệch chuẩn của Test Macro-F1 (đặc biệt quan trọng với `random`) |
| `test_mcc` | float | Điểm MCC trung bình trên tập Test |
| `test_f1_max` | float | Điểm Test Macro-F1 cao nhất đạt được qua các lượt chạy |
| `test_infer_s` | float | Thời gian suy luận trung bình đo với 150 cây cố định |

---

## 5. HƯỚNG DẪN TRÍCH XUẤT NHANH BẰNG PYTHON

### 5.1. Đọc và lấy các nghiệm đã chọn của NSGA-II v2
```python
import pandas as pd

# Đọc kết quả NSGA-II v2 Seed 44 trên DataSense
df = pd.read_csv("results/v2_ds_s44/final_eval.csv")

# Lọc nghiệm chọn theo quy tắc
selected = df[df["selected"].notna()]
print(selected[["solution", "n_features", "reduction_%", "test_macro_f1", "test_mcc", "selected"]])
```

### 5.2. So sánh NSGA-II với các Baseline v2 tại các mốc $k$
```python
import pandas as pd

df_base = pd.read_csv("results/v2_base_datasense_s44/baselines_summary.csv")
k_targets = [15, 20, 25]
pivot = df_base[df_base["k"].isin(k_targets)].pivot(index="k", columns="method", values="test_f1")
print(pivot[["all", "boruta_lite", "lgbm_imp", "mi", "random"]].round(4))
```

### 5.3. Nạp mặt nạ nhị phân của các nghiệm Pareto
```python
import numpy as np

pareto_mask = np.load("results/v2_ds_s44/pareto_X.npy")
print(f"Kích thước ma trận nghiệm Pareto: {pareto_mask.shape}")
print(f"Số đặc trưng từng nghiệm: {pareto_mask.sum(axis=1)}")
```

---

## 6. BẢO TOÀN DỮ LIỆU VÀ TÍNH TÁI LẬP (REPRODUCIBILITY)
- Mọi kết quả v2 trong thư mục này được sinh tự động từ hai kịch bản nguồn đặt tại `../data/`:
  1. `data/nsga2_fs.py`: Sinh ra các thư mục `v2_ds_s<seed>/` và `v2_nfuq_s<seed>/`.
  2. `data/baselines.py`: Sinh ra các thư mục `v2_base_datasense_s<seed>/` và `v2_base_nfuq_s<seed>/`.
- Các tệp nhị phân `.npy`, `.pkl` và `.csv` không được sửa đổi thủ công nhằm đảm bảo tính liêm chính và khách quan tuyệt đối theo quy tắc nghiên cứu khoa học tại [AGENTS.md](../AGENTS.md).
