# PROGRESS — Nhóm 9 — cập nhật lần cuối: 2026-10-28 14:35 bởi Agent

## Trạng thái hiện tại
- Tuần: 3 / 10   Giai đoạn: Tiền xử lý dữ liệu & Thiết lập môi trường đo lường
- Tình trạng so với lịch: Kỹ thuật dữ liệu và code lõi đang vượt tiến độ; Báo cáo tuần 2 đang bị chậm (cần gửi bù); Môi trường Docker E1/E2 cần hoàn thiện trong tuần này
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

### Tuần 3 (Tuần hiện tại)
| Việc | Người phụ trách | Hạn | Trạng thái | Sản phẩm (file) | Ghi chú |
|---|---|---|---|---|---|
| Module LightGBM wrapper, hàm chấm điểm chung | Danh | T4 | ✅ Xong | `data/common.py` | Đã xong và kiểm thử |
| Xuất Parquet, kiểm tra rò rỉ | Nam | T4 | ✅ Xong | `data/*.parquet` | Đã có 71 và 39 đặc trưng |
| Baseline All, Random, MI, LGBM Importance | Nam | T5 | ✅ Xong | `results/base_*_s42/` | Đã có số liệu chạy thử |
| Cài đặt Docker, dựng container E1 & E2 | Nhật | T6 | 🔄 Cần làm | `Dockerfile`, `scripts/` | Cần nhóm hỗ trợ |
| Script benchmark (warm-up 10, lặp 30) | Nhật | T7 | 🔄 Cần làm | `scripts/benchmark_edge.py` | Đo latency/RAM |
| Báo cáo tiến độ Tuần 2 & Tuần 3 cho GVHD | Nam (T2), Nhật (T3) | CN | 🔄 Cần làm | `BaoCao_Tuan2_Nhom9.docx` | Soạn gửi Thầy |

## Bàn giao giữa các bạn
| Từ | Cho | Sản phẩm | Hạn | Đã giao? |
|---|---|---|---|---|
| Nam | Danh | File Parquet sạch DataSense 10s & NF-UQ | T2 | ✅ Đã giao (`data/*.parquet`) |
| Danh | Nam, Nhật | Module `common.py` và hàm chấm điểm | T3 | ✅ Đã giao (`data/common.py`) |
| Nhật | Cả nhóm | Môi trường Docker E1/E2 & script đo | T3 | ⏳ Đang làm trong tuần 3 |

## Vấn đề phát sinh / bị chặn
- **Máy chưa có Docker:** Cần cài đặt `docker.io` trên máy Ubuntu hoặc viết script thay thế chuẩn Linux (`os.sched_setaffinity` cho CPU, `tracemalloc` cho RAM) để Nhật kịp tiến độ Tuần 3.
- **Tiến độ báo cáo:** Báo cáo Tuần 2 chưa gửi Thầy Phước, cần gửi ngay đầu tuần này và chuẩn bị tiếp Báo cáo Tuần 3.

## Quyết định đã chốt
- 2026-10-19: Chọn cửa sổ 10 giây (30.030 mẫu, 71 đặc trưng) cho DataSense IIoT 2025.
- 2026-10-19: Chia dữ liệu DataSense theo trục thời gian trong từng kịch bản (60% train / 20% val / 20% test).
- 2026-10-19: Cố định 150 cây cho LightGBM khi đo kiểm đối chứng baseline để bảo đảm so sánh thời gian công bằng.
- 2026-10-19: Hoàn thiện đề cương chi tiết v6 (`DeCuong_DeTai_DACN_Nhom9_v6.docx`).
- 2026-10-28: Thêm quy tắc làm việc AI Agent (`AGENTS.md`) và khởi tạo `PROGRESS.md`.
- 2026-10-28: Hoàn tất bản vá mã nguồn toàn diện: tách `common.py`, cố định hàm `evaluate_solution` 150 cây, lưu `cache.pkl` ra đĩa, kiểm tra cứng $d \in (71, 39)$, sửa lỗi resume checkpoint và cố định labels tính Macro-F1.
- 2026-10-28: Chốt lại vai trò nhóm đúng theo `AGENTS.md`, xác định hiện tại đang ở Tuần 3 của học kỳ.

## Báo cáo tuần
| Tuần | Chủ biên | Đã gửi GVHD? | Phản hồi của GVHD |
|---|---|---|---|
| Tuần 1 | Danh | Đã soạn (`BaoCao_Tuan1_Nhom9.docx`) | Đã hoàn tất tệp |
| Tuần 2 | Nam | Đang soạn bù | Chuẩn bị gửi |
| Tuần 3 | Nhật | Đến hạn cuối tuần này | Chuẩn bị |
