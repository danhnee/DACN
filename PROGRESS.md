# PROGRESS — Nhóm 9 — cập nhật lần cuối: 2026-11-01 23:00 bởi Agent

## Trạng thái hiện tại
- Tuần: 4 / 10   Giai đoạn: Chạy thực nghiệm đa mục tiêu NSGA-II chính thức & Đánh giá đối chứng
- Tình trạng so với lịch: Đúng và vượt tiến độ kỹ thuật; Hoàn tất báo cáo tuần 2 & tuần 3; Đã khắc phục an toàn sự cố phần cứng ổ đĩa.
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
- Báo cáo: Đã tạo `BaoCao_Tuan1_Nhom9.docx`

### Tuần 2 (Kỹ thuật đã xong - Cần chốt gửi báo cáo)
- Danh: Thiết kế bài toán pymoo, mã hóa nhị phân, 3 hàm mục tiêu, quy tắc chọn nghiệm ✅ (trong `nsga2_fs.py` & `common.py`)
- Nam: Thống kê dữ liệu, lấy mẫu phân tầng NF-UQ, chia DataSense theo thời gian ✅ (trong `prepare_data.py`, `prepare_datasense.py`)
- Nhật: Đối chiếu mục 4-5 của [3], tìm hiểu Dockerfile và cgroups ✅
- Báo cáo Tuần 2: Cần soạn và gửi GVHD bù ngay

### Tuần 3 (Đã hoàn thành 100%)
| Việc | Người phụ trách | Hạn | Trạng thái | Sản phẩm (file) | Ghi chú |
|---|---|---|---|---|---|
| Module LightGBM wrapper, hàm chấm điểm chung | Danh | T4 | ✅ Xong | `data/common.py` | Chuẩn hóa 150 cây, auto-detect nhãn |
| Xuất Parquet, kiểm tra rò rỉ | Nam | T4 | ✅ Xong | `data/*.parquet` | Đã có 71 và 39 đặc trưng |
| Baseline All, Random, MI, LGBM Importance | Nam | T5 | ✅ Xong | `results/base_*_s42/` | Đã có bảng số liệu đối chứng |
| Giả lập E1/E2 độc lập bằng Linux taskset/affinity | Nhật | T6 | ✅ Xong | `scripts/benchmark_edge.py` | Hoàn thành độc lập không cần Docker |
| Script benchmark (warm-up 10, lặp 30) | Nhật | T7 | ✅ Xong | `scripts/benchmark_edge.py` | Đo latency và peak RAM trên E1/E2 |
| Báo cáo tiến độ Tuần 3 cho GVHD | Nhật (Chủ biên), Danh | CN | ✅ Xong | `BaoCao_Tuan3_Nhom9.docx` | Đã xuất file và soạn thảo email |

## Bàn giao giữa các bạn
| Từ | Cho | Sản phẩm | Hạn | Đã giao? |
|---|---|---|---|---|
| Nam | Danh | File Parquet sạch DataSense 10s & NF-UQ | T2 | ✅ Đã giao (`data/*.parquet`) |
| Danh | Nam, Nhật | Module `common.py` và hàm chấm điểm | T3 | ✅ Đã giao (`data/common.py`) |
| Nhật | Cả nhóm | Môi trường giả lập E1/E2 & script đo chuẩn | T3 | ✅ Đã giao (`scripts/benchmark_edge.py`) |

## Vấn đề phát sinh / đã giải quyết
- **Máy chưa có Docker / Xung đột daemon:** Đã giải quyết triệt để bằng `scripts/benchmark_edge.py` dùng trực tiếp `os.sched_setaffinity` và `tracemalloc`, chạy trực tiếp trên Linux chuẩn mực mà không cần root.
- **Sự cố ổ cứng HDD:** Đã kịp thời di chuyển toàn bộ tài sản mã nguồn, kết quả và báo cáo sang ổ SSD chính `/home/danh/dacn/` và nén 2 bản dự phòng `.tar.gz`, `.zip`.
- **Tiến độ báo cáo:** Đã hoàn tất cả `BaoCao_Tuan2_Nhom9.docx` và `BaoCao_Tuan3_Nhom9.docx` sẵn sàng gửi Thầy Phước.

## Quyết định đã chốt
- 2026-10-19: Chọn cửa sổ 10 giây (30.030 mẫu, 71 đặc trưng) cho DataSense IIoT 2025.
- 2026-10-19: Chia dữ liệu DataSense theo trục thời gian trong từng kịch bản (60% train / 20% val / 20% test).
- 2026-10-19: Cố định 150 cây cho LightGBM khi đo kiểm đối chứng baseline để bảo đảm so sánh thời gian công bằng.
- 2026-10-19: Hoàn thiện đề cương chi tiết v6 (`DeCuong_DeTai_DACN_Nhom9_v6.docx`).
- 2026-10-28: Thêm quy tắc làm việc AI Agent (`AGENTS.md`) và khởi tạo `PROGRESS.md`.
- 2026-10-28: Hoàn tất bản vá mã nguồn toàn diện: tách `common.py`, cố định hàm `evaluate_solution` 150 cây, lưu `cache.pkl` ra đĩa, kiểm tra cứng $d \in (71, 39)$, sửa lỗi resume checkpoint và cố định labels tính Macro-F1.
- 2026-10-28: Chốt lại vai trò nhóm đúng theo `AGENTS.md`.
- 2026-11-01: Hoàn tất script đo lường biên `scripts/benchmark_edge.py` và hoàn thành `BaoCao_Tuan3_Nhom9.docx`.

## Báo cáo tuần
| Tuần | Chủ biên | Đã gửi GVHD? | Phản hồi của GVHD |
|---|---|---|---|
| Tuần 1 | Danh | Đã soạn (`BaoCao_Tuan1_Nhom9.docx`) | Đã hoàn tất |
| Tuần 2 | Nam | Đã soạn (`BaoCao_Tuan2_Nhom9.docx`) | Sẵn sàng gửi |
| Tuần 3 | Nhật | Đã soạn (`BaoCao_Tuan3_Nhom9.docx`) | Sẵn sàng gửi |
