# THƯ MỤC KẾT QUẢ THỰC NGHIỆM (`results/`)

Thư mục này lưu trữ toàn bộ các tệp kết quả thực nghiệm, nhật ký chạy máy (logs), checkpoint trạng thái và các mô hình Pareto thu được trong đề tài:
> **"Lựa chọn đặc trưng đa mục tiêu bằng NSGA-II cho hệ thống phát hiện xâm nhập trên thiết bị tài nguyên hạn chế"**  
> **Nhóm thực hiện:** Nhóm 9 (Nguyễn Thành Danh, Vũ Đức Nam, Nguyễn Minh Nhật)  
> **GVHD:** ThS. Nguyễn Trọng Minh Hồng Phước

---

## 1. CÂY CẤU TRÚC THƯ MỤC

```text
results/
├── README.md                      # [Tệp này] Tài liệu mô tả chi tiết các tệp và chức năng
├── ds_s42/                        # Kết quả chạy NSGA-II chính thức trên DataSense (Seed 42, 20 gen)
│   ├── final_eval.csv             # Bảng đánh giá chi tiết 24 nghiệm Pareto trên Val & Test
│   ├── pareto_F.npy               # Mảng mục tiêu (f1, f2, f3) của các nghiệm không trội
│   ├── pareto_X.npy               # Vector nhị phân mặt nạ đặc trưng của các nghiệm Pareto
│   ├── pop.npy                    # Toàn bộ quần thể cá thể ở thế hệ cuối cùng
│   └── state.json                 # Checkpoint trạng thái tiến hóa thuật toán
├── ds_s42.log                     # Log chi tiết quá trình chạy 20 thế hệ NSGA-II trên DataSense
│
├── base_ds_s42/                   # Kết quả đối chứng Baseline trên DataSense (Cố định số cây)
│   ├── baselines_eval.csv         # Chi tiết từng lượt chạy (gồm 10 runs ngẫu nhiên mỗi k)
│   └── baselines_summary.csv      # Bảng tổng hợp gom theo phương pháp và số đặc trưng k
├── base_ds_s42.log                # Log chi tiết quá trình huấn luyện và đánh giá Baseline DataSense
│
├── base_nfuq_s42/                 # Kết quả đối chứng Baseline trên NF-UQ-NIDS-v2 (Seed 42)
│   ├── baselines_eval.csv         # Chi tiết từng lượt chạy trên tập kiểm chứng NF-UQ
│   └── baselines_summary.csv      # Bảng tổng hợp theo phương pháp trên NF-UQ
│
├── test_datasense_10sec/          # Đợt chạy thử nghiệm sơ bộ NSGA-II trên DataSense (8 pop, 2 gen)
│   ├── final_eval.csv
│   ├── pareto_F.npy
│   ├── pareto_X.npy
│   ├── pop.npy
│   └── state.json
│
├── test_nfuqnids/                 # Đợt chạy thử nghiệm sơ bộ NSGA-II trên NF-UQ-NIDS-v2 (8 pop, 2 gen)
│   ├── final_eval.csv
│   ├── pareto_F.npy
│   ├── pareto_X.npy
│   ├── pop.npy
│   └── state.json
│
├── base_datasense_s42/            # Kết quả đợt chạy baseline đối chứng đầu tiên trên DataSense
│   ├── baselines_eval.csv
│   └── baselines_summary.csv
└── base_ds_quick/                 # Đợt chạy thử nghiệm baseline nhanh (smoke test)
    ├── baselines_eval.csv
    └── baselines_summary.csv
```

---

## 2. MÔ TẢ CHI TIẾT CÁC THƯ MỤC VÀ TỆP TIN CHÍNH

### 2.1. Thực nghiệm NSGA-II trên DataSense (`ds_s42/` & `ds_s42.log`)
* **Mục đích:** Lưu trữ kết quả của đợt chạy tối ưu đa mục tiêu chọn đặc trưng chính thức trên bộ dữ liệu **DataSense IIoT 2025** (cửa sổ 10 giây, 71 đặc trưng số ban đầu).
* **Cấu hình thực nghiệm:**
  - Thuật toán: NSGA-II (`pymoo`).
  - Quần thể: $N = 24$ cá thể.
  - Số thế hệ: $G = 20$ thế hệ (tổng cộng 480 lần đánh giá hàm mục tiêu).
  - Seed ngẫu nhiên: 42.
  - 3 mục tiêu: $f_1 = 1 - \text{Macro-F1 (Val)}$, $f_2 = |S|/d$, $f_3 = t_{pred}$ (đo trên $2.000$ mẫu Val, lặp 3 lần lấy trung vị).
* **Các tệp bên trong:**
  - `final_eval.csv`: Tệp quan trọng nhất. Đánh giá toàn bộ 24 nghiệm không trội trên tập Validation và tập Test độc lập. Trong đó đánh dấu rõ:
    + `pareto_4`: Nghiệm chọn theo ngưỡng $\delta = 1\%$ trên Validation ($k=21$ đặc trưng, giảm 70,4%, Test Macro-F1 = 0,9593 / 0,9601).
    + `pareto_23`: Nghiệm cân bằng *Knee Balanced* ($k=25$ đặc trưng, giảm 64,8%, Test Macro-F1 = 0,9700 / 0,9732).
  - `pareto_F.npy`: Mảng NumPy kích thước `(24, 3)` chứa giá trị 3 hàm mục tiêu của 24 nghiệm Pareto.
  - `pareto_X.npy`: Mảng boolean NumPy kích thước `(24, 71)` chứa vector nhị phân (chọn/bỏ) tương ứng của từng nghiệm.
  - `pop.npy`: Mảng NumPy lưu toàn bộ cá thể quần thể thế hệ thứ 20.
  - `state.json`: Checkpoint lưu vết trạng thái của thuật toán để có thể resume nếu gặp sự cố.
  - `ds_s42.log`: Nhật ký chạy, ghi nhận tiến trình từng thế hệ, số lượng cache và thời gian huấn luyện.

---

### 2.2. Thực nghiệm Baseline đối chứng DataSense (`base_ds_s42/` & `base_ds_s42.log`)
* **Mục đích:** Đánh giá đối chứng công bằng giữa NSGA-II và các phương pháp chọn lọc đặc trưng kinh điển trên cùng tập dữ liệu DataSense, cùng seed 42, và **cố định số cây** (`n_estimators = 150`, không dùng early stopping để tránh làm sai lệch thời gian suy luận).
* **Các phương pháp so sánh:**
  1. `all`: Mô hình sử dụng toàn bộ 71 đặc trưng ($k=71$).
  2. `random`: Chọn ngẫu nhiên $k$ đặc trưng (chạy lặp lại 10 lần độc lập cho mỗi giá trị $k$ để lấy kỳ vọng và độ lệch chuẩn).
  3. `mi`: Xếp hạng đặc trưng theo Mutual Information (Filter).
  4. `lgbm_imp`: Xếp hạng đặc trưng theo độ quan trọng Gain của LightGBM (Embedded).
  5. `boruta_lite`: Phương pháp Boruta rút gọn sử dụng đặc trưng bóng (Shadow features).
  6. `nsga2`: Đánh giá lại toàn bộ các nghiệm Pareto của NSGA-II trong cùng điều kiện số cây cố định.
* **Các tệp bên trong:**
  - `baselines_eval.csv`: Dữ liệu thô của từng lần chạy đơn lẻ (gồm tất cả các lần chạy ngẫu nhiên, từng nghiệm Pareto, từng mức $k$).
  - `baselines_summary.csv`: Dữ liệu đã gộp nhóm theo `(method, k)` báo cáo giá trị trung bình (`test_f1`), độ lệch chuẩn (`test_f1_std`), F1 lớn nhất (`test_f1_max`) và thời gian suy luận (`test_infer_s`).
  - `base_ds_s42.log`: Nhật ký chi tiết của script `baselines.py`.

---

### 2.3. Thực nghiệm kiểm chứng trên NF-UQ-NIDS-v2 (`base_nfuq_s42/` & `test_nfuqnids/`)
* **Mục đích:** Kiểm chứng tính khái quát của phương pháp trên bộ dữ liệu luồng thuần NetFlow (**NF-UQ-NIDS-v2**, 39 đặc trưng số, 21 lớp tấn công, 167.820 mẫu sau lấy mẫu phân tầng).
* **Các tệp bên trong:**
  - `base_nfuq_s42/baselines_eval.csv` & `baselines_summary.csv`: Kết quả đối chứng giữa All Features (39 đặc trưng), LightGBM Importance, MI, Random Selection (10 runs) và các nghiệm NSGA-II trên NF-UQ.
  - `test_nfuqnids/`: Chứa các tệp mô hình Pareto ban đầu (`pareto_X.npy`, `pareto_F.npy`, `final_eval.csv`) từ đợt chạy thử nghiệm trên NF-UQ.

---

### 2.4. Các thư mục chạy thử nghiệm phụ
* **`test_datasense_10sec/`**: Đợt chạy thử nghiệm pipeline ban đầu (quần thể 8 cá thể, 2 thế hệ) trên DataSense để xác nhận mã nguồn không lỗi trước khi chạy chính thức.
* **`base_datasense_s42/` & `base_ds_quick/`**: Các đợt chạy baseline kiểm tra tham số sơ bộ (smoke test) trong giai đoạn tinh chỉnh mã nguồn.

---

## 3. TỪ ĐIỂN DỮ LIỆU CÁC CỘT (DATA DICTIONARY)

### 3.1. Cấu trúc tệp `final_eval.csv` (trong thư mục NSGA-II)
| Cột | Kiểu dữ liệu | Ý nghĩa |
| :--- | :---: | :--- |
| `solution` | string | Định danh nghiệm Pareto (ví dụ: `pareto_0`, `pareto_4`, `baseline_all`) |
| `n_features` | integer | Số lượng đặc trưng được chọn ($|S|$) |
| `reduction_%` | float | Tỷ lệ giảm số chiều: $\frac{d - |S|}{d} \times 100\%$ |
| `val_macro_f1` | float | Điểm Macro-F1 đánh giá trên tập Validation |
| `val_mcc` | float | Hệ số tương quan Matthews (MCC) trên tập Validation |
| `val_infer_s` | float | Thời gian suy luận trung vị (giây) trên tập mẫu Validation |
| `test_macro_f1` | float | Điểm Macro-F1 đánh giá trên tập Test độc lập |
| `test_mcc` | float | Điểm MCC trên tập Test độc lập |
| `test_infer_s` | float | Thời gian suy luận (giây) trên toàn bộ tập Test |
| `selected` | string | Đánh dấu nghiệm được chọn: `chosen_delta(0.01)` hoặc `knee_balanced` |
| `features` | string | Danh sách tên các đặc trưng được chọn (phân cách bằng dấu chấm phẩy `;`) |

---

### 3.2. Cấu trúc tệp `baselines_summary.csv` (trong thư mục Baseline)
| Cột | Kiểu dữ liệu | Ý nghĩa |
| :--- | :---: | :--- |
| `method` | string | Tên phương pháp: `all`, `random`, `mi`, `lgbm_imp`, `boruta_lite`, `nsga2` |
| `k` | integer | Số lượng đặc trưng được chọn |
| `runs` | integer | Số lần chạy thực nghiệm độc lập (với `random` là 10, các phương pháp khác là 1) |
| `val_f1` | float | Macro-F1 trung bình trên tập Validation |
| `test_f1` | float | Macro-F1 trung bình trên tập Test |
| `test_f1_std` | float | Độ lệch chuẩn của Test Macro-F1 (đặc biệt quan trọng với `random`) |
| `test_mcc` | float | MCC trung bình trên tập Test |
| `test_f1_max` | float | Macro-F1 lớn nhất đạt được qua các lần chạy |
| `test_infer_s` | float | Thời gian suy luận đo được với số cây cố định |

---

## 4. HƯỚNG DẪN ĐỌC VÀ TRÍCH XUẤT NHANH KẾT QUẢ BẰNG PYTHON

### 4.1. Đọc và lọc nghiệm đã chọn của NSGA-II trên DataSense
```python
import pandas as pd

# Đọc kết quả NSGA-II
df = pd.read_csv("ds_s42/final_eval.csv")

# Lọc các nghiệm được chọn theo quy tắc
selected = df[df["selected"].notna()]
print(selected[["solution", "n_features", "reduction_%", "test_macro_f1", "test_mcc", "selected"]])
```

### 4.2. So sánh NSGA-II với các Baseline ở cùng số lượng đặc trưng $k$
```python
import pandas as pd

df_base = pd.read_csv("base_ds_s42/baselines_summary.csv")

# Xem so sánh ở k = 21 và k = 25
k_targets = [21, 25, 37]
subset = df_base[df_base["k"].isin(k_targets)].pivot(
    index="k", columns="method", values="test_f1"
)
print(subset[["all", "random", "mi", "lgbm_imp", "boruta_lite", "nsga2"]])
```

### 4.3. Đọc mặt nạ đặc trưng (Feature Mask) từ file `.npy`
```python
import numpy as np

# Đọc mặt nạ nhị phân của các nghiệm Pareto
pareto_mask = np.load("ds_s42/pareto_X.npy")
print(f"Kích thước ma trận nghiệm Pareto: {pareto_mask.shape}") # (24 nghiệm, 71 đặc trưng)

# Số đặc trưng được chọn của từng nghiệm
features_count = pareto_mask.sum(axis=1)
print(f"Số đặc trưng từng nghiệm: {features_count}")
```

---

## 5. BẢO TOÀN DỮ LIỆU VÀ TÍNH TÁI LẬP (REPRODUCIBILITY)
- Mọi kết quả trong thư mục này được sinh ra hoàn toàn tự động từ hai kịch bản nguồn đặt tại thư mục `../data/`:
  1. `nsga2_fs.py`: Sinh ra các thư mục `ds_s42/`, `test_datasense_10sec/`, `test_nfuqnids/`.
  2. `baselines.py`: Sinh ra các thư mục `base_ds_s42/`, `base_nfuq_s42/`.
- Không chỉnh sửa thủ công các tệp `.csv` hoặc `.npy` để bảo đảm tính liêm chính và khách quan tuyệt đối của dữ liệu nghiên cứu khoa học.
