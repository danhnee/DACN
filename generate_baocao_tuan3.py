import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import shutil
import os

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = docx.Document()
    
    # Page setup - Margins
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(0.8)

    # Base style
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.2
    normal_style.paragraph_format.space_after = Pt(4)

    # Header section
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst1 = p_inst.add_run("TRƯỜNG ĐẠI HỌC CÔNG NGHỆ TP. HỒ CHÍ MINH (HUTECH)\n")
    r_inst1.bold = True
    r_inst1.font.size = Pt(12)
    r_inst2 = p_inst.add_run("KHOA CÔNG NGHỆ THÔNG TIN\n")
    r_inst2.bold = True
    r_inst2.font.size = Pt(12)
    r_div = p_inst.add_run("-------------------***-------------------")
    r_div.bold = True

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(2)
    r_t1 = p_title.add_run("BÁO CÁO TIẾN ĐỘ THỰC HIỆN ĐỒ ÁN CHUYÊN NGÀNH\n")
    r_t1.bold = True
    r_t1.font.size = Pt(15)
    r_t1.font.color.rgb = RGBColor(0, 32, 96) # Dark Blue

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_after = Pt(12)
    r_t2 = p_sub.add_run("TUẦN 3: XÂY DỰNG MODULE CHUẨN HÓA ĐÁNH GIÁ, THỰC NGHIỆM ĐỐI CHỨNG BASELINES VÀ THIẾT LẬP MÔI TRƯỜNG BIÊN\n")
    r_t2.bold = True
    r_t2.font.size = Pt(12.5)
    r_t2.font.color.rgb = RGBColor(192, 0, 0) # Dark Red

    # Project Info
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_after = Pt(12)
    r_m = p_meta.add_run(
        "• Đề tài: Lựa chọn đặc trưng đa mục tiêu bằng NSGA-II cho hệ thống phát hiện xâm nhập trên thiết bị tài nguyên hạn chế\n"
        "• Giảng viên hướng dẫn: ThS. Nguyễn Trọng Minh Hồng Phước\n"
        "• Nhóm thực hiện: Nhóm 9 (Nguyễn Thành Danh - Trưởng nhóm, Vũ Đức Nam, Nguyễn Minh Nhật)\n"
        "• Thời gian báo cáo: Tuần 3 (Từ 26/10/2026 đến 01/11/2026)"
    )
    r_m.font.italic = True
    r_m.font.size = Pt(11)

    # Section I
    p_s1 = doc.add_paragraph()
    p_s1.paragraph_format.space_before = Pt(8)
    r_s1 = p_s1.add_run("I. MỤC TIÊU CÔNG VIỆC TRONG TUẦN 3")
    r_s1.bold = True
    r_s1.font.size = Pt(13)

    p_s1_body = doc.add_paragraph()
    p_s1_body.add_run(
        "Căn cứ theo kế hoạch 10 tuần trong đề cương chi tiết v7 và bảng phân công nhiệm vụ đồ án, các mục tiêu trọng tâm trong Tuần 3 gồm:\n"
        "1. Thành viên Danh (Trưởng nhóm, Lõi NSGA-II): Xây dựng module dùng chung data/common.py nhằm chuẩn hóa toàn diện quy trình tải dữ liệu, cấu hình bộ phân lớp LightGBM wrapper, hàm chấm điểm đồng nhất 150 cây và phòng vệ rò rỉ đặc trưng. Đồng thời, vá lỗi cơ chế lưu cache ra đĩa kèm băm cấu hình, sửa lỗi resume checkpoint và chuẩn hóa cách tính nghiệm Knee ổn định.\n"
        "2. Thành viên Nam (Kỹ thuật dữ liệu & Baseline): Kiểm định chất lượng 2 tập Parquet sạch (DataSense IIoT 71 đặc trưng và NF-UQ-NIDS-v2 39 đặc trưng); lập trình và chạy thực nghiệm bộ phương pháp đối chứng Baseline (All features, Random Selection lặp 20 lần/k độc lập RNG, Mutual Information, LightGBM Gain Importance, Boruta-Lite); tổng hợp bảng dữ liệu so sánh ban đầu.\n"
        "3. Thành viên Nhật (Chủ biên Tuần 3, Đo lường & Môi trường biên): Nghiên cứu và hiện thực hóa môi trường giả lập biên E1 (1 vCPU) và E2 (2 vCPU) bằng cơ chế Linux CPU Affinity trong tiến trình con độc lập; đo lường độ trễ (warm-up 10 lần, đo 30 lần báo cáo trung vị Median và khoảng tứ phân vị IQR), đo bộ nhớ RSS đỉnh thực tế (ru_maxrss) và dung lượng tệp mô hình lưu trữ."
    )

    # Section II
    p_s2 = doc.add_paragraph()
    p_s2.paragraph_format.space_before = Pt(10)
    r_s2 = p_s2.add_run("II. KẾT QUẢ CÁC CÔNG VIỆC CHÍNH ĐÃ HOÀN THÀNH")
    r_s2.bold = True
    r_s2.font.size = Pt(13)

    # Sub-item 1
    p_s2_1 = doc.add_paragraph()
    r_s2_1 = p_s2_1.add_run("1. Hoàn thiện Module Chuẩn Hóa và Nâng Cấp Bộ Lõi Đánh Giá (Danh phụ trách):")
    r_s2_1.bold = True
    p_s2_1_c = doc.add_paragraph()
    p_s2_1_c.add_run(
        "• Tách biệt kiến trúc thành module trung tâm data/common.py: Gom các hàm cốt lõi (load_split, make_model, evaluate_solution, measure_infer_time) vào một nguồn duy nhất, giải quyết triệt để nguy cơ phân kỳ quy trình giữa nsga2_fs.py và baselines.py.\n"
        "• Chuẩn hóa số cây đánh giá: Cố định 150 cây cho LightGBM (n_estimators=150) cho mọi mô hình đánh giá cuối cùng, bảo đảm tính công bằng tuyệt đối và khả năng tái lập cao khi đối chiếu thời gian suy luận và điểm Macro-F1.\n"
        "• Chuẩn hóa mẫu đo thời gian: Đổi từ việc lấy 5.000 dòng đầu sang lấy mẫu ngẫu nhiên cố định (default_rng(0)) N = 5.000 dòng trên cả tập Validation và Test, đảm bảo cùng một lát cắt dữ liệu cho mọi nghiệm Pareto và mọi baseline.\n"
        "• Chuẩn hóa tính toán Macro-F1 & Kiểm tra nhãn: Thiết lập tham số cứng labels=classes và zero_division=0 trong hàm tính Macro-F1; bổ sung cảnh báo thiếu lớp và cơ chế kiểm tra nhãn nghiêm ngặt (dừng chương trình nếu tham số --label không tồn tại).\n"
        "• Tối ưu cơ chế Checkpoint & Cache của NSGA-II: Lưu trữ bộ đệm ra đĩa (cache.pkl) kèm băm cấu hình (kích thước dữ liệu, seed, số lớp, số cây fitness) để tự động hủy cache khi đổi tham số; khắc phục triệt để lỗi mất 1 thế hệ khi resume (done > 0 cộng thêm 1 vào termination và bỏ qua tăng done ở lượt khởi tạo); chuẩn hóa điểm Knee tính trên (f1, f2) với cận cố định [0, 1] đến điểm lý tưởng (0, 0), loại bỏ nhiễu thời gian thực."
    )

    # Sub-item 2
    p_s2_2 = doc.add_paragraph()
    r_s2_2 = p_s2_2.add_run("2. Hiện Thực Hóa và Chạy Thực Nghiệm Đối Chứng Baselines (Nam phụ trách):")
    r_s2_2.bold = True
    p_s2_2_c = doc.add_paragraph()
    p_s2_2_c.add_run(
        "• Đã hiện thực đầy đủ 5 phương pháp đối chứng baseline trong data/baselines.py theo đúng đề cương:\n"
        "  + All Features: Giữ toàn bộ đặc trưng số (71 đặc trưng DataSense, 39 đặc trưng NF-UQ).\n"
        "  + Random Selection: Thử nghiệm ngẫu nhiên với 20 lần lặp độc lập (runs=20) cho mỗi mức k in {5, 10, 15, ..., 50}, khởi tạo bộ sinh số ngẫu nhiên độc lập default_rng([seed, k, r]) và lưu trữ đầy đủ mặt nạ đặc trưng.\n"
        "  + Mutual Information (MI): Lọc top k đặc trưng có thông tin tương hỗ cao nhất với nhãn.\n"
        "  + LightGBM Feature Importance: Lọc top k đặc trưng theo độ lợi phân nhánh (split gain) sau khi huấn luyện trên tập Train.\n"
        "  + Boruta rút gọn (Boruta-Lite): Tạo đặc trưng giả (shadow features), chạy phân loại và dùng kiểm định thống kê kết hợp sắp xếp đa tiêu chí (lexsort) theo số lần thắng và độ lợi gain.\n"
        "• Kết quả thực nghiệm đối chứng sơ bộ trên DataSense IIoT 2025 (đo kiểm đồng nhất 150 cây trên cùng mẫu 5.000 dòng):"
    )

    # Add Table of results
    table = doc.add_table(rows=6, cols=6)
    table.style = 'Table Grid'
    headers = ["Phương pháp", "Số đặc trưng (k)", "Tỷ lệ giảm (%)", "Val Macro-F1", "Test Macro-F1", "Test Infer (s)"]
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        hdr_cells[i].paragraphs[0].runs[0].bold = True
        hdr_cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_margins(hdr_cells[i], top=80, bottom=80, left=100, right=100)

    rows_data = [
        ["All Features (Gốc)", "71", "0.0%", "0.9682", "0.9745", "1.952s"],
        ["Boruta-Lite (k=25)", "25", "64.8%", "0.9675", "0.9740", "1.890s"],
        ["LGBM Importance (k=25)", "25", "64.8%", "0.9674", "0.9707", "1.854s"],
        ["Random (k=25, 20 runs)", "25", "64.8%", "0.9412", "0.9521 ± 0.012", "1.865s"],
        ["NSGA-II Knee (Đã chuẩn hóa)", "25", "64.8%", "0.9654", "0.9736", "1.840s"]
    ]
    for r_idx, row in enumerate(rows_data):
        cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=80, right=80)
            if c_idx in [1, 2, 3, 4, 5]:
                cells[c_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    p_tbl_note = doc.add_paragraph()
    r_tn = p_tbl_note.add_run("(* Ghi chú: Thời gian suy luận được đo kiểm đồng nhất qua hàm evaluate_solution trên cùng lát cắt ngẫu nhiên 5.000 mẫu của tập Test, lặp 5 lần lấy trung vị)")
    r_tn.font.size = Pt(10)
    r_tn.font.italic = True

    # Sub-item 3
    p_s2_3 = doc.add_paragraph()
    p_s2_3.paragraph_format.space_before = Pt(6)
    r_s2_3 = p_s2_3.add_run("3. Thiết Lập Môi Trường Biên và Kịch Bản Benchmark Chuẩn Hóa (Nhật phụ trách):")
    r_s2_3.bold = True
    p_s2_3_c = doc.add_paragraph()
    p_s2_3_c.add_run(
        "• Phương án giả lập tài nguyên biên: Do việc cấp quyền daemon Docker trên máy phát triển cá nhân gặp xung đột phân quyền, nhóm đã xây dựng giải pháp thay thế kỹ thuật chuẩn mực scripts/benchmark_edge.py sử dụng giao diện nhân Linux:\n"
        "  + Giả lập CPU: Sử dụng cơ chế Linux CPU Affinity trong tiến trình con độc lập (os.sched_setaffinity) để khóa cứng tiến trình vào đúng 1 nhân CPU (E1: core 0) và 2 nhân CPU (E2: core 0, 1).\n"
        "  + Đo bộ nhớ RSS đỉnh thực tế: Sử dụng resource.RUSAGE_SELF.ru_maxrss trong tiến trình riêng chỉ nạp mô hình đã lưu để đo chính xác tổng bộ nhớ Resident Set Size (bao gồm cả mã C++ của LightGBM và cây quyết định).\n"
        "  + Chỉ số độ trễ: Thực hiện 10 lần warm-up, đo 30 lần lặp độc lập trên mẫu 5.000 dòng cố định, báo cáo giá trị Trung vị (Median) và Khoảng tứ phân vị (IQR = Q75 - Q25) để loại bỏ ảnh hưởng của xung đột CPU đột xuất.\n"
        "• Bảng kết quả benchmark thực tế trên môi trường biên (trích xuất từ results/edge_benchmark_summary.csv):"
    )

    # Add Table of Edge Benchmark
    table2 = doc.add_table(rows=7, cols=7)
    table2.style = 'Table Grid'
    headers2 = ["Mô hình", "Số đặc trưng (k)", "Cấu hình biên", "Batch size", "Độ trễ trung vị", "IQR (ms)", "Peak RSS (KB)"]
    hdr_cells2 = table2.rows[0].cells
    for i, h in enumerate(headers2):
        hdr_cells2[i].text = h
        hdr_cells2[i].paragraphs[0].runs[0].bold = True
        hdr_cells2[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_margins(hdr_cells2[i], top=80, bottom=80, left=80, right=80)

    rows_data2 = [
        ["All Features", "71 (100%)", "E1 (1 CPU)", "Batch 1 (Streaming)", "0.451 ms", "0.236 ms", "305,756 KB"],
        ["All Features", "71 (100%)", "E1 (1 CPU)", "Batch 1024 (Batch)", "353.874 ms", "191.506 ms", "305,756 KB"],
        ["All Features", "71 (100%)", "E2 (2 CPU)", "Batch 1024 (Batch)", "186.849 ms", "58.998 ms", "305,756 KB"],
        ["NSGA-II Knee", "25 (35.2%)", "E1 (1 CPU)", "Batch 1 (Streaming)", "0.810 ms", "0.380 ms", "305,756 KB"],
        ["NSGA-II Knee", "25 (35.2%)", "E1 (1 CPU)", "Batch 1024 (Batch)", "352.823 ms", "70.900 ms", "305,756 KB"],
        ["NSGA-II Knee", "25 (35.2%)", "E2 (2 CPU)", "Batch 1024 (Batch)", "244.793 ms", "194.909 ms", "305,756 KB"]
    ]
    for r_idx, row in enumerate(rows_data2):
        cells = table2.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=80, right=80)
            if c_idx in [1, 3, 4, 5, 6]:
                cells[c_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Sub-item 4
    p_s2_4 = doc.add_paragraph()
    p_s2_4.paragraph_format.space_before = Pt(6)
    r_s2_4 = p_s2_4.add_run("4. Kiểm Định Rò Rỉ Dữ Liệu và Sự Cố Ổ Đĩa:")
    r_s2_4.bold = True
    p_s2_4_c = doc.add_paragraph()
    p_s2_4_c.add_run(
        "• Kiểm định shortcut và rò rỉ (scripts/check_shortcuts.py): Đã kiểm tra xác nhận cả 2 bộ dữ liệu không có cột hằng; tỷ lệ trùng lặp vector đặc trưng Test trong Train ở DataSense cực thấp (1.74%); quét toàn bộ các đặc trưng đơn lẻ đều cho Macro-F1 < 0.70 (chứng minh không có shortcut đơn lẻ thao túng bài toán); thử nghiệm bỏ 7 đặc trưng log trên DataSense cho thấy 64 đặc trưng mạng vẫn đạt Test F1 0.9727 (chênh lệch chỉ 0.0011), khẳng định mô hình học đúng bản chất mạng.\n"
        "• Sự cố ổ đĩa HDD: Ổ đĩa phụ gặp bad sector, nhóm đã di chuyển toàn bộ dữ liệu sạch, mã nguồn đã vá, báo cáo và kết quả thực nghiệm sang phân vùng SSD an toàn (/home/danh/dacn/), tạo 2 bản nén lưu trữ độc lập (7.4 MB) và dọn dẹp Git repo về 7.6 MB chuẩn bị đẩy lên GitHub."
    )

    # Section III
    p_s3 = doc.add_paragraph()
    p_s3.paragraph_format.space_before = Pt(10)
    r_s3 = p_s3.add_run("III. ĐÁNH GIÁ MỨC ĐỘ HOÀN THÀNH TIẾN ĐỘ TUẦN 3")
    r_s3.bold = True
    r_s3.font.size = Pt(13)

    p_s3_body = doc.add_paragraph()
    p_s3_body.add_run(
        "• Đánh giá chung: Hoàn thành 100% mục tiêu của Tuần 3 theo đúng đề cương chi tiết v7.\n"
        "• Hệ thống mã nguồn đã được module hóa chặt chẽ (common.py), quy trình đánh giá 150 cây được thống nhất tuyệt đối giữa NSGA-II và các Baseline.\n"
        "• Đã có đầy đủ kết quả baseline thực nghiệm để làm căn cứ đối sánh khoa học cho thuật toán NSGA-II.\n"
        "• Môi trường biên E1 và E2 đã được kiểm chứng hoạt động ổn định và đo đạc chuẩn xác qua script benchmark độc lập.\n"
        "• Toàn bộ các nghi vấn về rò rỉ dữ liệu và lỗi checkpoint đã được giải quyết triệt để bằng kiểm thử phần mềm."
    )

    # Section IV
    p_s4 = doc.add_paragraph()
    p_s4.paragraph_format.space_before = Pt(10)
    r_s4 = p_s4.add_run("IV. CÁC VẤN ĐỀ TỒN ĐỌNG VÀ GIẢI PHÁP")
    r_s4.bold = True
    r_s4.font.size = Pt(13)

    p_s4_body = doc.add_paragraph()
    p_s4_body.add_run(
        "1. Về giới hạn tài nguyên RAM trên môi trường biên: Hiện tại os.sched_setaffinity chỉ mới giới hạn số nhân CPU mà chưa khống chế cứng trần RAM vật lý (512MB/1GB). Nhóm đã ghi nhận đây là thay đổi kỹ thuật tạm thời so với đề cương ban đầu và đang nghiên cứu tích hợp lệnh systemd-run --scope -p MemoryMax=512M hoặc cấu hình nhóm Docker chính thức trong Tuần 4.\n"
        "2. Vấn đề tương quan độ phẳng của f3 theo số đặc trưng k: Do số cây cố định 60 khi tính fitness, thời gian suy luận phụ thuộc nhiều vào cấu trúc cây hơn là số đặc trưng. Nhóm sẽ ghi nhận chi tiết hiện tượng này và phân tích hệ số tương quan Pearson trong nội dung nghiên cứu ở Tuần 4."
    )

    # Section V
    p_s5 = doc.add_paragraph()
    p_s5.paragraph_format.space_before = Pt(10)
    r_s5 = p_s5.add_run("V. KẾ HOẠCH CÔNG VIỆC TRONG TUẦN 4")
    r_s5.bold = True
    r_s5.font.size = Pt(13)

    p_s5_body = doc.add_paragraph()
    p_s5_body.add_run(
        "Bước sang giai đoạn chạy thực nghiệm toàn diện và phân tích sâu kết quả, nhóm đề ra kế hoạch Tuần 4:\n"
        "• Thành viên Danh: Tiến hành chạy chính thức NSGA-II trên 5-6 seed độc lập cho bộ dữ liệu DataSense IIoT 2025; thu thập tập nghiệm Pareto Front và trích xuất các nghiệm tiêu biểu (Knee, delta-tolerance 1%, 2%).\n"
        "• Thành viên Nam: Triển khai chạy NSGA-II và Baselines trên bộ dữ liệu mạng NetFlow NF-UQ-NIDS-v2 (167.820 mẫu); lập trình script vẽ biểu đồ phân tán Pareto đa mục tiêu và biểu đồ hộp (boxplot) so sánh phân phối Macro-F1.\n"
        "• Thành viên Nhật: Áp dụng script benchmark_edge.py hoàn thiện khâu đo kiểm RAM với systemd-run MemoryMax trên môi trường E1 và E2; tổng hợp số liệu cho Bảng kết quả so sánh trong báo cáo Tuần 4."
    )

    # Signatures
    p_sign = doc.add_paragraph()
    p_sign.paragraph_format.space_before = Pt(18)
    p_sign.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_place = p_sign.add_run("TP. Hồ Chí Minh, ngày 01 tháng 11 năm 2026\n")
    r_place.font.italic = True
    r_role = p_sign.add_run("ĐẠI DIỆN NHÓM SINH VIÊN THỰC HIỆN\n\n\n\n")
    r_role.bold = True
    r_names = p_sign.add_run("Nguyễn Minh Nhật (Chủ biên Tuần 3) & Nguyễn Thành Danh (Trưởng nhóm)")
    r_names.bold = True

    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BaoCao_Tuan3_Nhom9.docx")
    doc.save(output_path)
    print(f"Report generated successfully at: {output_path}")

    # Copy to /home/danh/Downloads if exists
    downloads_dir = "/home/danh/Downloads"
    if os.path.exists(downloads_dir):
        shutil.copy(output_path, os.path.join(downloads_dir, "BaoCao_Tuan3_Nhom9.docx"))
        print(f"Copied to {downloads_dir}/ successfully.")

if __name__ == "__main__":
    create_report()
