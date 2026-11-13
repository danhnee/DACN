# PROGRESS — Nhóm 9 — cập nhật lần cuối: 2026-11-12 21:30 bởi Agent

## Trạng thái hiện tại
- Tuần: 5 / 10   Giai đoạn: Phân tích thực nghiệm đa seed v2 & Chuẩn hóa đối chứng baseline
- Workspace chính: `/mnt/EEAADB20AADAE3DD/Users/Danh/Documents/dacn/` (Windows: `C:\Users\Danh\Documents\dacn\`). Đây là phân vùng NTFS dùng chung giữa Linux và Windows được thống nhất làm nơi làm việc duy nhất. *Lưu ý: Phân vùng NTFS dùng chung qua Linux driver có thể gây sai lệch độ trễ I/O đĩa, cần ghi nhận khi phân tích số đo thời gian.*
- Tình trạng so với lịch: trễ 4 ngày (Về báo cáo tuần: Báo cáo Tuần 4 quá hạn từ 08/11/2026 và Báo cáo Tuần 2 chưa gửi GVHD; Về thực nghiệm kỹ thuật: đúng tiến độ).
- Người đang dùng agent: Nguyễn Thành Danh (Lead)
- Trạng thái phân vai (Roles): Đã chốt theo đúng AGENTS.md:
  * Nguyễn Thành Danh: Lead, lõi NSGA-II
  * Vũ Đức Nam: Data & Baseline
  * Nguyễn Minh Nhật: Edge & Eval (môi trường E1/E2, đo lường, báo cáo)

## Đánh giá theo tuần của đề tài
### Tuần 1 (Đã hoàn thành 100%)
- Danh: Đọc [3], chốt 4 điểm khác biệt tính mới ✅
- Nam: Khảo sát cấu trúc DataSense và NF-UQ ✅
- Nhật: Khảo sát tài liệu, soạn đề cương chi tiết v6 ✅
- Báo cáo: Đã nộp `BaoCao_Tuan1_Nhom9.docx` ✅

### Tuần 2 (Kỹ thuật xong - Báo cáo nợ)
- Danh: Thiết kế bài toán pymoo, mã hóa nhị phân, 3 hàm mục tiêu, quy tắc chọn nghiệm ✅ (trong `nsga2_fs.py` & `common.py`)
- Nam: Thống kê dữ liệu, lấy mẫu phân tầng NF-UQ, chia DataSense theo thời gian ✅ (trong `prepare_data.py`, `prepare_datasense.py`)
- Nhật: Đối chiếu mục 4–5 của [3] ⏳ Chưa hoàn tất (thiếu file văn bản sản phẩm đối chiếu); Tìm hiểu Dockerfile và cgroups ✅
- Báo cáo Tuần 2: Chưa gửi GVHD (đã quá hạn nhiều tuần, cần hoàn thiện và gửi bù ngay).

### Tuần 3 (Kỹ thuật xong)
| Việc | Người phụ trách | Hạn | Trạng thái | Sản phẩm (file) | Ghi chú |
|---|---|---|---|---|---|
| Module LightGBM wrapper, hàm chấm điểm chung | Danh | T4 | ✅ Xong | `data/common.py` | Chuẩn hóa 150 cây, auto-detect nhãn |
| Xuất Parquet, kiểm tra rò rỉ | Nam | T4 | ✅ Xong | `data/*.parquet` | Đã có 71 và 39 đặc trưng |
| Baseline All, Random, MI, LGBM Importance | Nam | T5 | ✅ Xong | `results/base_*_s42/` | Bảng số liệu đối chứng ban đầu |
| Giả lập E1/E2 độc lập bằng Linux CPU affinity | Nhật | T6 | ✅ Xong | `scripts/benchmark_edge.py` | Giả lập 1 vCPU (E1) và 2 vCPUs (E2) |
| Script benchmark (warm-up 10, lặp 30) | Nhật | T7 | ✅ Xong | `scripts/benchmark_edge.py` | Đo latency và peak RAM sơ bộ (tracemalloc / RSS quy trình) |
| Báo cáo tiến độ Tuần 3 cho GVHD | Nhật (Chủ biên), Danh | CN | ✅ Xong | `BaoCao_Tuan3_Nhom9.docx` | Đã gửi mail GVHD |

### Tuần 4 (Hoàn tất thực nghiệm đa seed v2 - Báo cáo nợ)
| Việc | Người phụ trách | Hạn | Trạng thái | Sản phẩm (file) | Ghi chú |
|---|---|---|---|---|---|
| Chạy lại 5 baseline chuẩn hóa v2 (DataSense s42) | Nam, Danh | T2 | ✅ Xong | `results/v2_base_datasense_s42/` | 20 random runs/k |
| Chạy lại NSGA-II v2 (DataSense s42) | Danh | T3 | ✅ Xong | `results/v2_ds_s42/` | 480 evals; Delta: k=17 F1=0.9700; Knee: k=13 F1=0.9501 |
| Chạy lại 5 baseline chuẩn hóa v2 (NF-UQ s42) | Nam, Danh | T4 | ✅ Xong | `results/v2_base_nfuq_s42/` | 20 random runs/k |
| Chạy lại NSGA-II v2 trên NF-UQ (s42) | Danh | T4 | ✅ Xong | `results/v2_nfuq_s42/` | 477 evals; Delta: k=13 F1=0.8808; Knee: k=9 F1=0.8396 |
| Mở rộng thực nghiệm đa seed v2 | Danh, Nam | T5 | ✅ Xong | `results/` | DataSense s42–s47 (6 seeds); NF-UQ s42–s47 (6 seeds) |
| Đo hiệu năng biên E1/E2 với giới hạn RAM cứng | Nhật | T6 | ⏳ Kế hoạch | `results/edge_benchmark_summary_v2.csv` | Chờ giải pháp giới hạn RAM cứng (cgroup/Docker) |
| Báo cáo tiến độ Tuần 4 cho GVHD | Danh (Chủ biên) | CN 08/11 | ⏳ Quá hạn | `BaoCao_Tuan4_Nhom9.docx` | Cần soạn bù và gửi ngay trong Tuần 5 |

### Tuần 5 (Tuần hiện tại: 09/11 – 15/11/2026)
| Việc | Người phụ trách | Hạn | Trạng thái | Sản phẩm (file) | Ghi chú |
|---|---|---|---|---|---|
| Rà soát, kiểm định độc lập số liệu v2 (Bước 1) | Danh | T4 | ✅ Xong | Báo cáo kiểm tra bước 1 | Phát hiện sai lệch std k, lệch s42, và so sánh lệch k |
| Sửa đổi tài liệu đồng bộ PROGRESS.md & README (Bước 2) | Danh | T5 | 🔄 Đang làm | `PROGRESS.md`, `results/README.md` | Chuẩn hóa thông tin minh bạch, chính xác |
| Chạy Baseline đối chứng tại đúng k của NSGA-II (Bước 3) | Nam, Danh | T6 | ⏳ Chờ chạy | `results/v3_base_...` | Chạy 20 random runs/k, cùng seed, cùng k thực tế |
| Kiểm định thống kê Wilcoxon theo cặp cùng k | Danh | T7 | ⏳ Kế hoạch | Báo cáo p-value | Đối chứng có ý nghĩa thống kê giữa NSGA-II và Baselines |
| Hoàn thiện gửi Báo cáo Tuần 2 & Tuần 4 (bù) | Nam, Danh | T6 | ⏳ Cần làm | `BaoCao_Tuan2_Nhom9.docx`, `BaoCao_Tuan4_Nhom9.docx` | Gửi bù Thầy Phước |
| Soạn và gửi Báo cáo Tuần 5 | Nam (Chủ biên) | CN 15/11 | ⏳ Kế hoạch | `BaoCao_Tuan5_Nhom9.docx` | Đúng hạn Chủ nhật |

## Bàn giao giữa các bạn
| Từ | Cho | Sản phẩm | Hạn | Đã giao? |
|---|---|---|---|---|
| Nam | Danh | File Parquet sạch DataSense 10s & NF-UQ | T2 | ✅ Đã giao (`data/*.parquet`) |
| Danh | Nam, Nhật | Module `common.py` và hàm chấm điểm | T3 | ✅ Đã giao (`data/common.py`) |
| Nhật | Cả nhóm | Môi trường giả lập E1/E2 & script đo chuẩn | T3 | ✅ Đã giao (`scripts/benchmark_edge.py`) |
| Nhật | Cả nhóm | Tài liệu đối chiếu mục 4–5 của [3] | T2 (nợ) | ❌ Chưa giao (thiếu file) |

## Vấn đề phát sinh / đã giải quyết
- **Môi trường giả lập E1/E2 và giới hạn RAM:** Hiện tại dùng giải pháp thay thế bằng `scripts/benchmark_edge.py` sử dụng `os.sched_setaffinity` (CPU affinity: 1 core cho E1, 2 cores cho E2) và đo `ru_maxrss`/`tracemalloc`. Chưa có cơ chế giới hạn cứng RAM 512MB/1GB (chờ phản hồi của GVHD về giải pháp container Docker/cgroups).
- **Thống nhất không gian làm việc:** Sử dụng duy nhất phân vùng NTFS `/mnt/EEAADB20AADAE3DD/Users/Danh/Documents/dacn/` (Windows: `C:\Users\Danh\Documents\dacn\`) làm thư mục làm việc chính của dự án để đảm bảo tính đồng bộ giữa hai hệ điều hành dual-boot.
- **Tiến độ báo cáo tuần:** Nhóm đang nợ Báo cáo Tuần 2 và Tuần 4. Cần hoàn tất soạn thảo để gửi GVHD ngay trong tuần này.

## Quyết định đã chốt
- 2026-10-19: Chọn cửa sổ 10 giây (30.030 mẫu, 71 đặc trưng) cho DataSense IIoT 2025.
- 2026-10-19: Chia dữ liệu DataSense theo trục thời gian trong từng kịch bản (60% train / 20% val / 20% test).
- 2026-10-19: Cố định 150 cây cho LightGBM khi đo kiểm đối chứng baseline để bảo đảm so sánh thời gian công bằng.
- 2026-10-19: Hoàn thiện đề cương chi tiết v6 (`DeCuong_DeTai_DACN_Nhom9_v6.docx`).
- 2026-10-28: Thêm quy tắc làm việc AI Agent (`AGENTS.md`) và khởi tạo `PROGRESS.md`.
- 2026-10-28: Hoàn tất bản vá mã nguồn toàn diện: tách `common.py`, cố định hàm `evaluate_solution` 150 cây, lưu `cache.pkl` ra đĩa, kiểm tra cứng $d \in (71, 39)$, sửa lỗi resume checkpoint và cố định labels tính Macro-F1.
- 2026-10-28: Chốt lại vai trò nhóm đúng theo `AGENTS.md`.
- 2026-11-01: Hoàn tất script đo lường biên `scripts/benchmark_edge.py` và hoàn thành `BaoCao_Tuan3_Nhom9.docx`.
- 2026-11-06: Hoàn tất 10 bản vá A.1–A.10 (resume gen, băm cache, đo ngẫu nhiên 5k mẫu, Knee xác định trên $(f_1, f_2)$, độc lập random mask, whitelist 71 feats, chẩn đoán shortcut).
- 2026-11-06: Thống nhất chạy lại toàn bộ thuật toán mới (kết quả lưu `results/v2_...`, không ghi đè kết quả cũ) để đảm bảo tính nhất quán khoa học 100%.

## Quyết định đang chờ
1. **Ngưỡng $\delta = 1$ điểm phần trăm:** Chờ ý kiến chốt chính thức từ GVHD. *Lưu ý quan trọng:* Toàn bộ nghiệm chọn $\delta$ hiện tại đã được đánh giá trên tập test độc lập. Nếu GVHD yêu cầu đổi giá trị $\delta$, nghiệm mới bắt buộc phải được chọn lại thuần túy trên tập validation trước khi mở tập test để tránh nguy cơ rò rỉ dữ liệu (data snooping).
2. **Số lượng seed thực nghiệm:** Hiện nhóm đã chạy 6 seed trên DataSense (s42–s47) và 5 seed trên NF-UQ (s42–s46), trong khi đề cương đăng ký 5 seed (và cho phép giảm xuống 3 seed trên NF-UQ nếu chi phí cao). Cần xin ý kiến GVHD về việc giữ nguyên 6 seed DataSense / 5 seed NF-UQ hay cắt gọn về đúng 5 seed đồng nhất trong báo cáo nghiệm thu.
3. **Quy tắc xác định nghiệm Knee (Bản vá A.6):** Đã chuyển sang khoảng cách Euclid tới điểm lý tưởng $(0, 0)$ chỉ trên 2 mục tiêu chuẩn hóa $(f_1, f_2)$ và bỏ qua $f_3$. Lý do: $f_3$ bị chi phối bởi độ nhiễu đo lặp CPU của hệ điều hành, không có tương quan đơn điệu với số đặc trưng $k$. Cần ghi nhận và báo cáo GVHD.
4. **Mối tương quan $f_3$ ($t_{pred}$) theo $k$:** Kết quả thực nghiệm v2 chỉ ra $f_3$ có tương quan âm hoặc không có ý nghĩa thống kê với $k$ ($r = -0.17$ trên DataSense, $r = +0.09, p=0.35$ trên NF-UQ). Cần đưa hiện tượng này vào mục thảo luận/phân tích hạn chế của đề tài.
5. **Môi trường giả lập E1/E2:** Đang dùng CPU affinity (`os.sched_setaffinity`) thay vì container Docker/cgroups giới hạn cứng RAM 512MB/1GB; đang chờ phản hồi từ GVHD.

## Báo cáo tuần
| Tuần | Chủ biên | Đã gửi GVHD? | Phản hồi của GVHD |
|---|---|---|---|
| Tuần 1 | Danh | Đã nộp (`BaoCao_Tuan1_Nhom9.docx`) | Đã hoàn tất |
| Tuần 2 | Nam | Đã soạn nháp (`BaoCao_Tuan2_Nhom9.docx`) | Chưa gửi GVHD (quá hạn, cần gửi bù ngay) |
| Tuần 3 | Nhật | Đã nộp (`BaoCao_Tuan3_Nhom9.docx`) | Đã gửi mail GVHD |
| Tuần 4 | Danh | Chưa soạn (`BaoCao_Tuan4_Nhom9.docx`) | Quá hạn (hạn 08/11/2026, cần soạn bù) |
| Tuần 5 | Nam | Kế hoạch (`BaoCao_Tuan5_Nhom9.docx`) | Hạn Chủ nhật 15/11/2026 |
