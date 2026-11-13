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
├── v2_ds_s42/ ~ s47/                        # NSGA-II v2 trên DataSense (24 pop, 20 gen, 480 evals)
│   ├── final_eval.csv                       # Đánh giá các nghiệm Pareto trên Val & Test (150 cây cố định)
│   ├── pareto_F.npy                         # Ma trận 3 mục tiêu [1-F1, |S|/d, t_pred] của nghiệm không trội
│   ├── pareto_X.npy                         # Mặt nạ nhị phân boolean (chọn/bỏ) tương ứng của các nghiệm Pareto
│   ├── pop.npy                              # Quần thể cá thể ở thế hệ 20
│   ├── state.json                           # Checkpoint thế hệ {"gen": 20}
│   └── cache.pkl                            # Bộ nhớ đệm băm cấu hình config_meta
├── v2_base_datasense_s42/ ~ s47/            # 5 Baseline đối chứng v2 trên DataSense (10 mức k, 20 runs/k)
│   ├── baselines_eval.csv                   # Chi tiết từng lượt chạy đơn lẻ (gồm 20 runs random/k)
│   └── baselines_summary.csv                # Bảng tổng hợp theo phương pháp và số đặc trưng k
│
├── [THỰC NGHIỆM CHUẨN HÓA V2 - NF-UQ-NIDS-V2]
├── v2_nfuq_s42/ ~ s47/                      # NSGA-II v2 trên NF-UQ (167k mẫu, 21 lớp, 39 đặc trưng)
│   ├── final_eval.csv                       # Đánh giá chi tiết nghiệm Pareto trên Val & Test
│   ├── pareto_F.npy, pareto_X.npy           # Nghiệm không trội & mặt nạ nhị phân
│   ├── pop.npy, state.json, cache.pkl       # Checkpoint tiến hóa và bộ nhớ đệm
├── v2_base_nfuq_s42/ ~ s47/                 # 5 Baseline đối chứng v2 trên NF-UQ (7 mức k, 20 runs/k)
│   ├── baselines_eval.csv, baselines_summary.csv
│
├── [ĐO HIỆU NĂNG TRÊN THIẾT BỊ BIÊN GIẢ LẬP E1 / E2]
├── edge_benchmark_summary.csv               # Kết quả đo latency (IQR) và Peak RSS trên E1 giả lập (1 vCPU qua affinity core 0)
├── edge_benchmark_summary_E2.csv            # Kết quả đo latency và Peak RAM trên E2 giả lập (2 vCPUs qua affinity cores 0, 1)
│
└── [LƯU TRỮ LỊCH SỬ V1 (SMOKE TEST & CHẠY SƠ BỘ TRƯỚC VÁ MÃ NGUỒN)]
    ├── ds_s42/, base_ds_s42/, base_nfuq_s42/
    ├── test_datasense_10sec/, test_nfuqnids/
    └── base_datasense_s42/, base_ds_quick/
```

---

## 2. QUY CHUẨN THỰC NGHIỆM V2 (CHUẨN HÓA A.1 – A.10)

Để bảo đảm tính liêm chính và nhất quán khoa học 100%, toàn bộ kết quả trong các thư mục `v2_...` tuân thủ nghiêm ngặt 10 nguyên tắc sau:
1. **Mục tiêu $f_3$ (Thời gian suy luận):** Đo trên $2.000$ mẫu Validation ngẫu nhiên cố định (lấy bằng `rng.choice(len(Xva), 2000, replace=False)`) thay vì cắt lát tuần tự, lặp 3 lần lấy trung vị ($n\_jobs=1$). *Lưu ý: Mọi số đo thời gian ngoài E1/E2 đều ghi nhận nhãn "máy phát triển" (CPU Intel Core i3, không giới hạn CPU affinity).*
2. **Bảo vệ Cache bằng băm cấu hình (`config_meta`):** Checkpoint `cache.pkl` lưu kèm siêu dữ liệu cấu hình ($n\_var, n\_tr, n\_va, classes, seed, trees$), nếu khác biệt sẽ tự động tạo mới, ngăn chặn tuyệt đối dùng lẫn cache.
3. **Cơ chế khôi phục thế hệ chính xác:** Sửa lỗi lệch số vòng lặp khi resume trong `pymoo` (`remaining + 1` khi khôi phục checkpoint).
4. **Độc lập hạt giống ngẫu nhiên cho Baseline Random:** Khởi tạo `default_rng([seed, k, r])` độc lập hoàn toàn giữa các giá trị $k$ và lượt lặp $r$, loại bỏ hiện tượng tập con $k$ lớn bị phụ thuộc tập con $k$ nhỏ.
5. **Số lượt lặp Random:** Tăng lên **20 lượt chạy ngẫu nhiên độc lập** cho mỗi mức $k$ để báo cáo kỳ vọng và độ lệch chuẩn tin cậy.
6. **Xác định nghiệm Knee cân bằng:** Tính khoảng cách Euclid tới điểm lý tưởng $(0, 0)$ trên không gian chuẩn hóa $(f_1, f_2)$ với $f_1 = 1 - \text{Val F1} \in [0, 1]$ và $f_2 = |S|/d \in [0, 1]$ (loại bỏ $f_3$ khỏi khoảng cách Knee do $f_3$ bị chi phối bởi độ nhiễu đo lặp CPU).
7. **Cố định số cây đánh giá:** Toàn bộ nghiệm Pareto và các Baseline đều được đánh giá bằng LightGBM với **cố định 150 cây** (`n_estimators=150`, không early stopping).
8. **Đồng nhất số mức $k$ so sánh:**
   - **DataSense (71 đặc trưng):** 10 mức $k \in \{5, 10, 15, 20, 25, 30, 35, 40, 50, 60\}$.
   - **NF-UQ-NIDS-v2 (39 đặc trưng):** 7 mức $k \in \{5, 10, 15, 20, 25, 30, 35\}$.
9. **Bảo toàn tập Test:** Chỉ đánh giá tập Test đúng 1 lần cho báo cáo cuối cùng, không tham gia vào bất kỳ khâu chọn lọc đặc trưng hay chọn nghiệm nào.
10. **Tách biệt kết quả:** Toàn bộ kết quả mới lưu tại thư mục `v2_...`, không ghi đè dữ liệu cũ.

---

## 3. TỔNG HỢP SỐ LIỆU ĐA SEED V2 (SEEDS 42, 43, 44, 45, 46, 47)

### 3.1. Dữ liệu DataSense IIoT 2025 (71 đặc trưng, chia thời gian 60/20/20)
*Toàn bộ đặc trưng (`all`, $k=71$): Val Macro-F1 = 0.9700, Test Macro-F1 = **0.9738**, Test MCC = 0.9677.*

| Seed | Nghiệm | Số đặc trưng $k$ | Tỷ lệ giảm | Val Macro-F1 | Test Macro-F1 | Test MCC | Nguồn tệp CSV |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| **s42** | **Nghiệm chọn $\delta = 1\%$** | **17** | **76.1%** | **0.9611** | **0.9700** | **0.9581** | `v2_ds_s42/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 13 | 81.7% | 0.9468 | 0.9501 | 0.9416 | `v2_ds_s42/final_eval.csv` |
| **s43** | **Nghiệm chọn $\delta = 1\%$** | **23** | **67.6%** | **0.9651** | **0.9681** | **0.9619** | `v2_ds_s43/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 18 | 74.6% | 0.9273 | 0.9432 | 0.9300 | `v2_ds_s43/final_eval.csv` |
| **s44** | **Nghiệm chọn $\delta = 1\%$** | **18** | **74.6%** | **0.9630** | **0.9708** | **0.9605** | `v2_ds_s44/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 15 | 78.9% | 0.9274 | 0.9375 | 0.9274 | `v2_ds_s44/final_eval.csv` |
| **s45** | **Nghiệm chọn $\delta = 1\%$** | **19** | **73.2%** | **0.9623** | **0.9684** | **0.9624** | `v2_ds_s45/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 12 | 83.1% | 0.9298 | 0.9358 | 0.9341 | `v2_ds_s45/final_eval.csv` |
| **s46** | **Nghiệm chọn $\delta = 1\%$** | **24** | **66.2%** | **0.9606** | **0.9669** | **0.9617** | `v2_ds_s46/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 20 | 71.8% | 0.9514 | 0.9634 | 0.9545 | `v2_ds_s46/final_eval.csv` |
| **s47** | **Nghiệm chọn $\delta = 1\%$** | **17** | **76.1%** | **0.9649** | **0.9728** | **0.9625** | `v2_ds_s47/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 14 | 80.3% | 0.9340 | 0.9375 | 0.9321 | `v2_ds_s47/final_eval.csv` |
| **Trung bình** | **Nghiệm chọn $\delta = 1\%$** | **19.7 $\pm$ 3.1** | **72.3%** | **0.9628 $\pm$ 0.0019** | **0.9695 $\pm$ 0.0021** | **0.9612 $\pm$ 0.0017** | *(Tổng hợp 6 seed, ddof=1)* |

*(Ghi chú về độ lệch chuẩn: Nếu dùng độ lệch chuẩn tổng thể ddof=0, ta có: $k = 19.7 \pm 2.8$, Test Macro-F1 = $0.9695 \pm 0.0020$, Test MCC = $0.9612 \pm 0.0015$).*

**Đối chiếu sơ bộ với Baseline trên DataSense (Tổng hợp 6 seeds s42–s47):**
> ⚠️ **Lưu ý quan trọng về đối chứng Baseline:** Lưới $k$ cũ của Baseline ($\{5, 10, 15, 20, ...\}$) không chứa các giá trị $k$ thực tế của nghiệm $\delta$ NSGA-II ($k \in \{17, 18, 19, 23, 24\}$). Do đó, việc đặt cạnh Baseline tại $k=20$ dưới đây chỉ mang tính chất tham khảo sơ bộ. Theo quy định công bằng tại AGENTS.md Mục 4.2 (cùng $k$, cùng seed, cùng số cây), nhóm sẽ thực hiện chạy lại các Baseline tại đúng từng mức $k$ thực tế của từng nghiệm NSGA-II (lưu tại `results/v3_base_...`) trước khi thực hiện kiểm định Wilcoxon.

- **NSGA-II (Nghiệm $\delta$, $k \in \{17..24\}$, trung bình $k=19.7$):** Test Macro-F1 = **0.9695 $\pm$ 0.0021**
- **Đối chiếu tại mốc $k=20$ của Baseline (trung bình 6 seeds):**
  + **Boruta rút gọn ($k=20$):** 0.9684 *(chênh lệch so với NSGA-II $\Delta = +0.0011$, nhỏ hơn độ lệch chuẩn giữa các seed $\sigma = 0.0021$, do đó hiệu năng là tương đương)*
  + **LightGBM Gain ($k=20$):** 0.9687 *(chênh lệch $\Delta = +0.0008 < \sigma$, hiệu năng tương đương)*
  + **Mutual Information ($k=20$):** 0.9664
  + **Random Selection ($k=20$, 20 runs/seed):** 0.9498 $\pm$ 0.0120

---

### 3.2. Dữ liệu NF-UQ-NIDS-v2 (39 đặc trưng NetFlow, phân tầng 60/20/20)
*Toàn bộ đặc trưng (`all`, $k=39$): Val Macro-F1 = 0.8842, Test Macro-F1 = **0.8872**, Test MCC = 0.8921.*

| Seed | Nghiệm | Số đặc trưng $k$ | Tỷ lệ giảm | Val Macro-F1 | Test Macro-F1 | Test MCC | Nguồn tệp CSV |
|:---:|---|:---:|:---:|:---:|:---:|:---:|---|
| **s42** | **Nghiệm chọn $\delta = 1\%$** | **13** | **66.7%** | **0.8743** | **0.8808** | **0.8862** | `v2_nfuq_s42/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 9 | 76.9% | 0.8361 | 0.8396 | 0.8503 | `v2_nfuq_s42/final_eval.csv` |
| **s43** | **Nghiệm chọn $\delta = 1\%$** | **10** | **74.4%** | **0.8751** | **0.8765** | **0.8806** | `v2_nfuq_s43/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 6 | 84.6% | 0.8510 | 0.8543 | 0.8652 | `v2_nfuq_s43/final_eval.csv` |
| **s44** | **Nghiệm chọn $\delta = 1\%$** | **15** | **61.5%** | **0.8756** | **0.8812** | **0.8875** | `v2_nfuq_s44/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 7 | 82.1% | 0.8255 | 0.8314 | 0.8654 | `v2_nfuq_s44/final_eval.csv` |
| **s45** | **Nghiệm chọn $\delta = 1\%$** | **14** | **64.1%** | **0.8782** | **0.8821** | **0.8856** | `v2_nfuq_s45/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 5 | 87.2% | 0.8150 | 0.8223 | 0.8301 | `v2_nfuq_s45/final_eval.csv` |
| **s46** | **Nghiệm chọn $\delta = 1\%$** | **14** | **64.1%** | **0.8746** | **0.8797** | **0.8872** | `v2_nfuq_s46/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 6 | 84.6% | 0.8416 | 0.8489 | 0.8687 | `v2_nfuq_s46/final_eval.csv` |
| **s47** | **Nghiệm chọn $\delta = 1\%$** | **15** | **61.5%** | **0.8770** | **0.8818** | **0.8837** | `v2_nfuq_s47/final_eval.csv` |
| | Nghiệm cân bằng (Knee) | 7 | 82.1% | 0.8299 | 0.8343 | 0.8531 | `v2_nfuq_s47/final_eval.csv` |
| **Trung bình** | **Nghiệm chọn $\delta = 1\%$** | **13.5 $\pm$ 1.9** | **65.4%** | **0.8758 $\pm$ 0.0015** | **0.8804 $\pm$ 0.0021** | **0.8851 $\pm$ 0.0026** | *(Tổng hợp 6 seed, ddof=1)* |

*(Ghi chú về độ lệch chuẩn: Nếu dùng độ lệch chuẩn tổng thể ddof=0, ta có: $k = 13.5 \pm 1.7$, Test Macro-F1 = $0.8804 \pm 0.0019$, Test MCC = $0.8851 \pm 0.0024$).*

**Đối chiếu sơ bộ với Baseline trên NF-UQ-NIDS-v2 (Tổng hợp 6 seeds s42–s47):**
> ⚠️ **Lưu ý quan trọng về đối chứng Baseline:** Lưới $k$ cũ của Baseline ($\{5, 10, 15, 20, ...\}$) chỉ có mốc $k=10$ và $k=15$ trùng với một số seed, các mốc $k=13$ và $k=14$ chưa có dữ liệu đối chứng trực tiếp. Việc đặt cạnh Baseline tại $k=15$ dưới đây chỉ mang tính tham khảo sơ bộ:

- **NSGA-II (Nghiệm $\delta$, $k \in \{10..15\}$, trung bình $k=13.5$):** Test Macro-F1 = **0.8804 $\pm$ 0.0021**
- **Đối chiếu tại mốc $k=15$ của Baseline (trung bình 5 seeds):**
  + **Boruta rút gọn ($k=15$):** 0.8795 *(chênh lệch so với NSGA-II $\Delta = +0.0006 < \sigma$, hiệu năng tương đương)*
  + **LightGBM Gain ($k=15$):** 0.8806 *(chênh lệch $\Delta = -0.0005 < \sigma$, hiệu năng tương đương)*
  + **Mutual Information ($k=15$):** 0.8775
  + **Random Selection ($k=15$, 20 runs/seed):** 0.8465 $\pm$ 0.0210

---

### 3.3. Đo lường hiệu năng biên giả lập E1 / E2
- **Cơ chế mô phỏng phần cứng:** Trong tệp `scripts/benchmark_edge.py`, hàm `os.sched_setaffinity` được dùng trên Linux để gán tiến trình con vào đúng 1 nhân CPU vật lý (E1: core 0) và 2 nhân CPU (E2: cores 0, 1).
- **Hiện trạng về giới hạn RAM:** Script **chưa thực hiện giới hạn cứng RAM 512MB hoặc 1GB** bằng cgroups hay cờ `--memory` của container Docker.
- **Bản chất các số đo bộ nhớ:**
  - Tệp `edge_benchmark_summary.csv`: Cột `peak_rss_kb` ghi nhận đỉnh bộ nhớ vật lý RSS của toàn bộ tiến trình Python thông qua `resource.getrusage(resource.RUSAGE_SELF).ru_maxrss`, đạt giá trị ~305.756 kB (~305 MB) khi nạp mô hình và tập dữ liệu.
  - Tệp `edge_benchmark_summary_E2.csv`: Cột `peak_ram_kb` ghi nhận bộ nhớ cấp phát thêm bởi trình thông dịch Python thông qua `tracemalloc` (từ 8.2 kB đến 84.9 kB).
- **Ghi nhãn môi trường đo thời gian:** Toàn bộ các chỉ số thời gian suy luận trong `final_eval.csv` và `baselines_summary.csv` (`val_infer_s`, `test_infer_s`) đều được đo trên **máy phát triển** (CPU Intel Core i3, hệ điều hành tiêu chuẩn, không giới hạn CPU affinity hay RAM).

---

### 3.4. Cơ chế đánh giá cá thể và bộ nhớ đệm (480 vs 477 đánh giá thực tế)
- Thuật toán NSGA-II thiết lập 20 thế hệ với quần thể 24 cá thể, tương đương 480 lượt xử lý cá thể mỗi lần chạy seed.
- Script `data/nsga2_fs.py` kích hoạt `eliminate_duplicates=True` trong `pymoo` và lưu đệm băm `cache.pkl` (`self.cache[mask.tobytes()] = F`). Khi một tổ hợp mặt nạ nhị phân xuất hiện lặp lại do toán tử lai ghép hoặc đột biến từ các thế hệ trước, hàm đánh giá tự động tái sử dụng kết quả từ cache mà không gọi lại LightGBM.
- **Số lượng nghiệm duy nhất thực tế được huấn luyện:**
  - Trên **DataSense IIoT 2025** ($d=71$, không gian tổ hợp $2^{71} \approx 2.36 \times 10^{21}$): Không gian tìm kiếm rất lớn nên hầu như không có cá thể trùng lặp qua các thế hệ. Tất cả các seed s42, s43, s45, s46, s47 đều huấn luyện đủ 480 cá thể duy nhất (riêng seed 44 có 479 cá thể duy nhất, hit cache 1 lần).
  - Trên **NF-UQ-NIDS-v2** ($d=39$, không gian tổ hợp $2^{39} \approx 5.5 \times 10^{11}$, nhỏ hơn DataSense hơn 4 tỷ lần): Xác suất toán tử di truyền tái tạo lại một nghiệm cũ cao hơn. Cụ thể: Seed 42 có 477 cá thể duy nhất (3 lần hit cache), Seed 43 có 478, Seed 44 có 479, Seed 45 có 479, Seed 46 có 478.
- Cả 480 cá thể đều được đánh giá đầy đủ trong quá trình tiến hóa; số lượng 477 (thay vì 480) mô hình LightGBM huấn luyện thực tế tại s42 NF-UQ phản ánh đúng cơ chế cache hoạt động hiệu quả theo thiết kế.

---

## 4. TỪ ĐIỂN DỮ LIỆU CÁC CỘT (DATA DICTIONARY)

### 4.1. Cấu trúc tệp `final_eval.csv` (trong thư mục NSGA-II v2)
| Cột | Kiểu | Ý nghĩa | Môi trường đo (env) |
| :--- | :---: | :--- | :--- |
| `solution` | string | Tên định danh nghiệm: `pareto_0`, `pareto_1`, ..., `baseline_all` | — |
| `n_features` | integer | Số lượng đặc trưng được chọn ($k = |S|$) | — |
| `reduction_%` | float | Tỷ lệ giảm số chiều: $\frac{d - |S|}{d} \times 100\%$ | — |
| `val_macro_f1` | float | Điểm Macro-F1 trên tập Validation (mẫu số nhãn cố định) | Máy phát triển |
| `val_mcc` | float | Điểm Matthews Correlation Coefficient trên tập Validation | Máy phát triển |
| `val_infer_s` | float | Thời gian suy luận trung vị (giây) trên tập mẫu Validation | Máy phát triển (CPU i3, native) |
| `test_macro_f1` | float | Điểm Macro-F1 đánh giá trên tập Test độc lập | Máy phát triển |
| `test_mcc` | float | Điểm MCC trên tập Test độc lập | Máy phát triển |
| `test_infer_s` | float | Thời gian suy luận (giây) trên toàn bộ tập Test | Máy phát triển (CPU i3, native) |
| `selected` | string | Đánh dấu nghiệm chọn: `chosen_delta(0.01)` hoặc `knee_balanced` | — |
| `features` | string | Danh sách tên đặc trưng được chọn (phân cách bằng dấu chấm phẩy `;`) | — |

### 4.2. Cấu trúc tệp `baselines_summary.csv` (trong thư mục Baseline v2)
| Cột | Kiểu | Ý nghĩa | Môi trường đo (env) |
| :--- | :---: | :--- | :--- |
| `method` | string | Phương pháp: `all`, `boruta_lite`, `lgbm_imp`, `mi`, `random` | — |
| `k` | integer | Số lượng đặc trưng được chọn | — |
| `runs` | integer | Số lượt chạy độc lập (20 lượt với `random`, 1 lượt với các phương pháp khác) | — |
| `val_f1` | float | Điểm Macro-F1 trung bình trên tập Validation | Máy phát triển |
| `test_f1` | float | Điểm Macro-F1 trung bình trên tập Test độc lập | Máy phát triển |
| `test_f1_std` | float | Độ lệch chuẩn của Test Macro-F1 (đặc biệt quan trọng với `random`) | Máy phát triển |
| `test_mcc` | float | Điểm MCC trung bình trên tập Test | Máy phát triển |
| `test_f1_max` | float | Điểm Test Macro-F1 cao nhất đạt được qua các lượt chạy | Máy phát triển |
| `test_infer_s` | float | Thời gian suy luận trung bình đo với 150 cây cố định | Máy phát triển (CPU i3, native) |

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
