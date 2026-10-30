# AGENTS.md — Quy tắc làm việc cho AI agent (Đồ án chuyên ngành, Nhóm 9)

> Đặt file này ở thư mục gốc của repo. Có thể đổi tên thành `CLAUDE.md` nếu dùng Claude Code.
> Agent đọc file này ở đầu mỗi phiên làm việc, trước khi làm bất cứ việc gì.

## 0. Hai mục tiêu của agent

1. Giúp nhóm làm đúng đề cương, đúng tiến độ, số liệu đúng.
2. **Giúp người dùng luôn biết tiến trình đang ở đâu, không bỏ lỡ việc nào.** Việc này quan trọng ngang với việc viết code. Xem mục 5.

Ngôn ngữ giao tiếp mặc định: **tiếng Việt**. Thuật ngữ kỹ thuật giữ nguyên tiếng Anh (Macro-F1, Pareto front, checkpoint...).

---

## 1. Bối cảnh dự án

- **Tên đề tài:** Lựa chọn đặc trưng đa mục tiêu bằng NSGA-II cho hệ thống phát hiện xâm nhập trên thiết bị tài nguyên hạn chế.
- **Học phần:** Đồ án chuyên ngành, HK1 năm học 2026–2027, HUTECH. **GVHD:** ThS. Nguyễn Trọng Minh Hồng Phước.
- **Nhóm 9 và vai trò:**

| Thành viên | MSSV | Vai trò |
|---|---|---|
| Nguyễn Thành Danh | 2380600275 | Lead, lõi NSGA-II |
| Vũ Đức Nam | 2380614839 | Data & Baseline |
| Nguyễn Minh Nhật | 2380601551 | Edge & Eval (môi trường E1/E2, đo lường, báo cáo) |

- Người đang chat với agent là một trong ba thành viên. Nếu chưa biết là ai, hỏi một lần rồi ghi vào `PROGRESS.md`.
- Công trình gốc **[3]**: Firouzi et al., "DataSense: A Real-Time Sensor-Based Benchmark Dataset for Attack Analysis in IIoT with Multi-Objective Feature Selection", Electronics 14(20), 4095, 2025. Đề tài **không** xem việc dùng NSGA-II là điểm mới.

### Bốn điểm khác biệt của đề tài so với [3] (không được làm lệch)

1. Đưa thời gian suy luận đo thực tế (t_pred) của LightGBM vào hàm mục tiêu.
2. Wrapper trực tiếp trên không gian đặc trưng đầu vào, không qua gom nhóm thủ công và Sparse Group Lasso.
3. Quy trình đo chuẩn hóa trong container giới hạn tài nguyên và quy tắc chọn nghiệm cố định trên validation.
4. Thực nghiệm đối chứng công bằng với baseline ở cùng số đặc trưng và cùng ngân sách t_pred.

---

## 2. Thiết kế kỹ thuật đã chốt trong đề cương (không tự ý đổi)

| Hạng mục | Giá trị |
|---|---|
| Bài toán | Chọn tập con đặc trưng, mã hóa nhị phân độ dài d (1 giữ, 0 bỏ) |
| Thuật toán | NSGA-II (pymoo), quần thể 24 cá thể, 20 thế hệ, tối đa 480 lần đánh giá mỗi seed; lai ghép, đột biến lật bit, chọn lọc theo hạng không trội và crowding distance |
| f1 | 1 − Macro-F1 trên validation |
| f2 | \|S\| / d (tỷ lệ đặc trưng được chọn) |
| f3 | t_pred, thời gian suy luận đo thực tế trên tập validation cố định |
| Bộ phân lớp | LightGBM (cây nhỏ khi đánh giá cá thể; huấn luyện lại cấu hình đầy đủ cho nghiệm cuối) |
| Dữ liệu 1 | DataSense IIoT 2025, cửa sổ 10 giây: 30.030 mẫu, d = 71, chia **theo thời gian** 60/20/20 (18.377 / 5.836 / 5.817) |
| Dữ liệu 2 | NF-UQ-NIDS-v2: lấy mẫu phân tầng tối đa ~10.000 mẫu mỗi lớp (167.820 dòng), 39 đặc trưng, chia **phân tầng** 60/20/20 |
| Môi trường đo | Container Docker/cgroups: E1 (1 CPU, 512 MB RAM), E2 (2 CPU, 1 GB RAM); warm-up 10 lần, lặp 30 lần, N = 5.000 mẫu cố định, batch 1 và batch 1024 |
| Baseline | Toàn bộ đặc trưng, Random Selection (≥ 10 lần), Mutual Information, LightGBM Feature Importance, Boruta rút gọn (dùng đặc trưng bóng, không dùng BorutaPy gốc) |
| Số seed | 5 seed; NF-UQ có thể giảm xuống 3 nếu chi phí vượt dự kiến |
| Chọn nghiệm | Trên **validation**: nghiệm không trội có ít đặc trưng nhất mà Macro-F1 không thấp hơn mô hình toàn bộ quá δ (δ = 1 điểm phần trăm, **chờ chốt với GVHD**); thêm nghiệm cân bằng (Knee) |
| Tập test | Chỉ dùng **một lần** để báo cáo, không dùng để chọn nghiệm |
| Chỉ số | Macro-F1 (chính), MCC, Feature Reduction (%), Inference Time; kiểm định Wilcoxon |
| Phân biệt đại lượng | t_pred = thời gian dự đoán của LightGBM; t_total = t_extract + t_pred. Đề tài chỉ đo t_pred |

Nếu yêu cầu của người dùng mâu thuẫn với bảng này, **nêu rõ mâu thuẫn và hỏi lại**, không tự đổi.

---

## 3. Lịch 10 tuần (theo đề cương; dấu * trong bảng gốc là tuần kết thúc)

| Hạng mục | Tuần | Phụ trách chính |
|---|---|---|
| Khảo sát DataSense gốc [3], làm rõ tính mới | 1–2 | Danh |
| Thống kê, lấy mẫu, tiền xử lý dữ liệu | 2–3 | Nam |
| Thiết lập môi trường giới hạn tài nguyên, quy trình đo | 3–4 | Nhật |
| Xây dựng baseline (toàn bộ, MI, Boruta, LightGBM) | 3–4 | Nam |
| Cài đặt, chạy thử NSGA-II, ước lượng chi phí | 4–5 | Danh |
| Chạy thực nghiệm hai bộ dữ liệu, nhiều seed | 5–8 | Danh (NSGA-II), Nam (baseline), Nhật (đo E1/E2) |
| Phân tích Pareto, chọn nghiệm validation, đánh giá test | 8–9 | Danh (chọn nghiệm), Nam (đánh giá test), Nhật (kiểm định, biểu đồ) |
| Viết báo cáo | 9–10 | Cả ba, mỗi người một chương |

Phân công chi tiết theo tuần nằm trong tài liệu "Phân công 10 tuần – Nhóm 9 (cân bằng theo đề cương)". Khi có thay đổi, cập nhật mục "Phân công theo tuần" của `PROGRESS.md`, không sửa bảng trên.

---

## 4. Quy tắc làm việc

### 4.1 Số liệu và tính trung thực (quan trọng nhất)

- **Không bịa số.** Mọi con số đưa vào văn bản (báo cáo, đề cương, slide) phải truy được về một file CSV hoặc log cụ thể. Ghi nguồn bên cạnh số (tên file, dòng).
- Trước khi sửa văn bản có số liệu, **đối chiếu lại với CSV/log gốc**. Từng có các lỗi lệch số do chép tay (Min 0,9271 so với 0,9305; 0,8824 so với 0,8828). Nếu thấy lệch, báo ngay.
- Kết quả của một seed hoặc lần chạy thử phải ghi rõ "sơ bộ, seed X, chỉ mang tính định hướng". Không gọi là "khẳng định".
- Nếu kết quả thực nghiệm đi ngược giả thuyết (ví dụ t_pred không phụ thuộc số đặc trưng), **báo cáo trung thực**, không làm đẹp.
- Không chép nguyên văn nội dung bài báo hoặc nguồn khác. Diễn đạt lại bằng lời của nhóm và trích dẫn.

### 4.2 Quy tắc thực nghiệm (tránh sai khoa học)

- Cố định seed, ghi seed vào tên thư mục kết quả. Mỗi kết quả phải chạy lại được bằng một lệnh.
- **Không dùng tập test để chọn đặc trưng, chọn nghiệm hay chỉnh tham số.** Test chỉ dùng cho báo cáo cuối.
- Không trộn các cửa sổ thời gian khác nhau của DataSense (cùng xuất phát từ một lưu lượng gốc, gây rò rỉ train/test).
- Không đưa cột định danh vào đặc trưng: tên thiết bị, MAC, IP, cổng, nhãn chi tiết, cột thời gian.
- Baseline và NSGA-II phải so sánh **cùng k, cùng seed, cùng dữ liệu, cùng cấu hình LightGBM**.
- Đo thời gian trong container E1/E2 và ghi rõ hồ sơ. Kết quả đo trên máy phát triển phải ghi nhãn "máy phát triển".
- Không sửa, ghi đè hay xóa dữ liệu gốc và kết quả đã chạy. Chỉ thêm file mới.

### 4.3 Code và file

- Mỗi giai đoạn có một thư mục riêng. Tên file kết quả có dạng `<dataset>_<method>_k<k>_seed<seed>.csv`.
- Quy ước cột CSV chung: `method, dataset, k, seed, val_macro_f1, test_macro_f1, mcc, t_pred, env`. Không đổi nếu chưa thống nhất cả nhóm.
- Mỗi script có docstring ngắn: đầu vào, đầu ra, cách chạy, thời gian chạy ước tính.
- Việc chạy lâu (NSGA-II nhiều seed) phải có checkpoint và log, và chạy từng việc một vì chỉ có một máy i3. Nói rõ ước tính thời gian trước khi chạy.
- Làm việc trên nhánh Git theo mảng (danh, nam, nhat). Không sửa trực tiếp mã của mảng khác mà không báo người phụ trách.

### 4.4 Khi nào hỏi, khi nào tự làm

**Tự làm, rồi báo lại:** sửa lỗi chính tả, định dạng, viết script phụ trợ, thống kê, vẽ biểu đồ từ CSV có sẵn.

**Phải hỏi trước:**
- đổi hàm mục tiêu, tham số NSGA-II, quy tắc chọn nghiệm hay δ;
- thêm hoặc bỏ baseline, đổi số seed;
- xóa hoặc ghi đè file;
- bất cứ việc gì làm thay đổi phạm vi so với đề cương;
- chạy lâu hơn 30 phút.

Khi hỏi: nêu 2 đến 3 lựa chọn, kèm khuyến nghị và lý do, tối đa một câu hỏi mỗi lần.

---

## 5. Theo dõi tiến trình (để người dùng không bỏ lỡ gì)

Agent duy trì file **`PROGRESS.md`** ở thư mục gốc. Đây là nguồn sự thật duy nhất về tiến độ. Mẫu ở mục 8.

### 5.1 Đầu mỗi phiên

Trước khi làm việc, agent đọc `AGENTS.md` và `PROGRESS.md`, rồi mở đầu bằng **bản tin trạng thái** ngắn (tối đa 10 dòng):

```
📍 Đang ở: Tuần X / 10 — giai đoạn <tên>
✅ Xong từ lần trước: ...
⏳ Đang làm: ...
⚠️ Trễ hoặc bị chặn: ...
📅 Sắp đến hạn (7 ngày tới): ...
👉 Đề xuất việc nên làm trong phiên này: ...
```

Nếu `PROGRESS.md` chưa có hoặc đã cũ quá 7 ngày, tạo hoặc hỏi người dùng cập nhật trước khi làm việc khác.

### 5.2 Cuối mỗi phiên (hoặc sau mỗi việc quan trọng)

Cập nhật `PROGRESS.md`: việc đã xong (kèm tên file sản phẩm), việc đang dở, điểm dừng, bước tiếp theo, vấn đề phát sinh. Báo người dùng đã cập nhật gì bằng một đoạn ngắn.

### 5.3 Cảnh báo chủ động

Agent **chủ động nhắc**, không chờ người dùng hỏi, khi:

- một việc quá hạn hoặc sắp quá hạn trong tuần;
- một việc của người khác đang chặn việc của người dùng, hoặc ngược lại (xem bảng bàn giao ở `PROGRESS.md`);
- đến hạn gửi **báo cáo tuần** (xem mục 6) hoặc họp nhóm;
- một việc chạy lâu đã xong, bị lỗi hoặc dừng giữa chừng;
- số liệu trong văn bản lệch với CSV;
- một quyết định đang chờ (δ, số seed NF-UQ, khung chương) chưa được chốt;
- tuần hiện tại có hạng mục trong lịch mà chưa ai bắt đầu.

Cách nhắc: một dòng, nói rõ việc gì, của ai, hạn khi nào, và đề xuất hành động tiếp theo.

### 5.4 Khi người dùng hỏi "đang đến đâu rồi?"

Trả lời theo đúng khung 5.1, thêm: phần trăm hoàn thành của tuần hiện tại, và so sánh với lịch ở mục 3 ("đúng tiến độ", "trễ N ngày", "vượt tiến độ").

---

## 6. Báo cáo tuần cho GVHD

- **Email:** To `ntmh.phuoc@hutech.edu.vn`; Cc email các thành viên trong nhóm. Tiêu đề: `[ĐACN HK1 26-27] BÁO CÁO ĐỒ ÁN TUẦN <N>`.
- **Nội dung email:** (1) Tên đề tài; (2) Các vấn đề chính đã thực hiện; (3) Các vấn đề còn tồn đọng; (4) QnA; (5) Đính kèm file báo cáo tuần (.docx).
- **File báo cáo:** `BaoCao_Tuan<N>_Nhom9.docx`, cấu trúc: I. Mục tiêu tuần; II. Kết quả đã hoàn thành; III. Đánh giá mức độ hoàn thành; IV. Vấn đề tồn đọng và khó khăn; V. Câu hỏi xin ý kiến.
- Báo cáo tuần xoay vòng người chủ biên. Agent soạn **bản nháp từ `PROGRESS.md`** vào cuối tuần.

### Kiểm tra bắt buộc trước khi chốt báo cáo tuần

1. **Chỉ báo cáo việc thuộc tuần đó** theo lịch ở mục 3. Việc của tuần sau, nếu đã làm trước, chỉ ghi một dòng "đã bắt đầu sớm". Không đưa kết quả chi tiết của tuần sau vào, kẻo báo cáo mâu thuẫn với kế hoạch.
2. Mục tiêu tuần ở phần I phải có kết quả tương ứng ở phần II, và ngược lại.
3. Mục IV không để trống; nếu không có tồn đọng thì ghi rõ "Không có".
4. Mọi số liệu đối chiếu được với CSV/log.
5. Đề cương và báo cáo không mâu thuẫn nhau (ví dụ báo cáo nói "đã đọc xong", đề cương nói "sẽ đọc").
6. Thuật ngữ thống nhất ("Boruta rút gọn", không trộn "Boruta-lite").

---

## 7. Điều cần theo dõi và các quyết định đang treo

Agent nhắc lại các mục này khi đến giai đoạn liên quan, và cập nhật trạng thái ở `PROGRESS.md`.

| Vấn đề | Trạng thái | Khi nào cần xử lý |
|---|---|---|
| **f3 = t_pred**: pilot cho thấy t_pred ít phụ thuộc số đặc trưng (Pearson r từ −0,69 đến +0,53 giữa các phương pháp). Cần kiểm chứng trong E1/E2 trước khi chạy chính thức | Mở | Tuần 4 (Nhật), trước khi chạy chính thức ở tuần 5–6 |
| Ngưỡng δ = 1 điểm phần trăm | Chờ chốt với GVHD | Trước tuần 8 |
| Số seed NF-UQ (3 hay 5) | Chờ nhóm quyết định, sau khi biết chi phí mỗi lần đánh giá | Tuần 5 |
| Đối chiếu mục 4–5 của [3] (tập đặc trưng được chọn, cách đo tài nguyên; có dùng Raspberry Pi để đo không) | Chưa xong | Tuần 2 (Nhật) |
| Khung chương báo cáo (đề xuất 6 chương) | Chờ nhóm đồng ý | Trước tuần 9 |
| Thứ tự đánh số tài liệu tham khảo trong đề cương (ví dụ [6] xuất hiện trước [1]) | Chưa sửa | Khi hoàn thiện báo cáo cuối |
| Chưa có thiết bị nhúng thật; dùng container để mô phỏng | Đã hỏi GVHD ở báo cáo tuần 1, chờ phản hồi | Ghi rõ hạn chế trong báo cáo cuối |

---

## 8. Mẫu `PROGRESS.md` (agent tạo nếu chưa có)

```markdown
# PROGRESS — Nhóm 9 — cập nhật lần cuối: <ngày giờ> bởi <người/agent>

## Trạng thái hiện tại
- Tuần: <N> / 10   Giai đoạn: <tên>
- Tình trạng so với lịch: <đúng tiến độ | trễ N ngày | vượt tiến độ>
- Người đang dùng agent: <tên>

## Tuần này (checklist)
| Việc | Người | Hạn | Trạng thái | Sản phẩm (file) | Người review |
|---|---|---|---|---|---|
| ... | Danh | T6 | ⬜ chưa / 🔄 đang / ✅ xong / ⛔ bị chặn | `path/file` | Nam |

## Bàn giao giữa các bạn
| Từ | Cho | Sản phẩm | Hạn | Đã giao? |
|---|---|---|---|---|

## Vấn đề phát sinh / bị chặn
- ...

## Quyết định đã chốt (kèm ngày)
- ...

## Quyết định đang chờ
- ...

## Nhật ký phiên làm việc (mới nhất ở trên)
- <ngày>: đã làm ..., điểm dừng ..., bước tiếp theo ...

## Báo cáo tuần
| Tuần | Chủ biên | Đã gửi GVHD? | Phản hồi của GVHD |
|---|---|---|---|
```

---

## 9. Phong cách trả lời

- Ngắn gọn, đi thẳng vào việc; đưa kết luận trước, chi tiết sau.
- Dùng bảng khi so sánh nhiều mục, dùng danh sách cho các bước tuần tự.
- Khi báo lỗi hoặc rủi ro, nói rõ: chuyện gì, ảnh hưởng gì, đề xuất xử lý.
- Khi không chắc, nói "chưa chắc" và nêu cách kiểm tra, không đoán.
- Không khen quá lời, không dùng icon trong tài liệu nộp cho GVHD. Icon chỉ dùng trong bản tin trạng thái nội bộ ở mục 5.1.
