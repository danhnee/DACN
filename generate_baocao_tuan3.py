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
        "Căn cứ theo kế hoạch 10 tuần trong đề cương chi tiết v6 và bảng phân công nhiệm vụ đồ án, các mục tiêu trọng tâm trong Tuần 3 gồm:\n"
        "1. Thành viên Danh (Trưởng nhóm, Lõi NSGA-II): Xây dựng module dùng chung data/common.py nhằm chuẩn hóa toàn diện quy trình tải dữ liệu, cấu hình bộ phân lớp LightGBM wrapper, hàm chấm điểm đồng nhất 150 cây và phòng vệ rò rỉ đặc trưng. Đồng thời, vá lỗi cơ chế lưu cache ra đĩa và khôi phục checkpoint của thuật toán NSGA-II.\n"
        "2. Thành viên Nam (Kỹ thuật dữ liệu & Baseline): Kiểm định chất lượng 2 tập Parquet sạch (DataSense IIoT 71 đặc trưng và NF-UQ-NIDS-v2 39 đặc trưng); lập trình và chạy thực nghiệm bộ phương pháp đối chứng Baseline (All features, Random Selection lặp 20 lần/k, Mutual Information, LightGBM Gain Importance, Boruta-Lite); tổng hợp bảng dữ liệu so sánh ban đầu.\n"
        "3. Thành viên Nhật (Chủ biên Tuần 3, Đo lường & Môi trường biên): Nghiên cứu và hiện thực hóa môi trường giả lập biên E1 (1 vCPU, 512MB RAM) và E2 (2 vCPU, 1GB RAM); giải quyết bài toán độc lập với Docker daemon bằng script benchmark chạy trực tiếp trên Linux (sử dụng os.sched_setaffinity / taskset và tracemalloc / psutil); thiết lập quy trình đo độ trễ suy luận chuẩn hóa (warm-up 10 lần, đo 30 lần trên batch size 1 và batch size 1024)."
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
        "• Chuẩn hóa tính toán Macro-F1: Thiết lập tham số cứng labels=classes và zero_division=0 trong hàm tính Macro-F1, loại bỏ hiện tượng thay đổi mẫu số do chia tập theo trục thời gian (khi tập Validation hoặc Test thiếu một số lớp tấn công hiếm).\n"
        "• Phòng vệ rò rỉ đặc trưng: Kiểm tra cứng kích thước vector đặc trưng d in {71, 39}, áp dụng danh sách loại trừ các cột định danh, nhãn phụ (device_name, device_mac, timestamp, label1, label3, label4...).\n"
        "• Tối ưu cơ chế Checkpoint & Cache của NSGA-II: Lưu trữ bộ đệm ra đĩa (cache.pkl) để tránh việc phải tính toán lại quần thể cũ khi chạy nối tiếp; khắc phục lỗi lệch số thế hệ termination=('n_gen', remaining + 1); đo thời gian suy luận f3 trên 2.000 mẫu Validation ngẫu nhiên cố định thay vì các dòng đầu kịch bản."
    )

    # Sub-item 2
    p_s2_2 = doc.add_paragraph()
    r_s2_2 = p_s2_2.add_run("2. Hiện Thực Hóa và Chạy Thực Nghiệm Đối Chứng Baselines (Nam phụ trách):")
    r_s2_2.bold = True
    p_s2_2_c = doc.add_paragraph()
    p_s2_2_c.add_run(
        "• Đã hiện thực đầy đủ 5 phương pháp đối chứng baseline trong data/baselines.py theo đúng đề cương:\n"
        "  + All Features: Giữ toàn bộ đặc trưng số (71 đặc trưng DataSense, 39 đặc trưng NF-UQ).\n"
        "  + Random Selection: Thử nghiệm ngẫu nhiên với 20 lần lặp độc lập (runs=20) cho mỗi mức k in {5, 10, 15, ..., 50}, tính trung bình và độ lệch chuẩn.\n"
        "  + Mutual Information (MI): Lọc top k đặc trưng có thông tin tương hỗ cao nhất với nhãn.\n"
        "  + LightGBM Feature Importance: Lọc top k đặc trưng theo độ lợi phân nhánh (split gain) sau khi huấn luyện trên tập Train.\n"
        "  + Boruta rút gọn (Boruta-Lite): Tạo đặc trưng giả (shadow features), chạy phân loại và dùng kiểm định thống kê kết hợp sắp xếp đa tiêu chí (lexsort) theo số lần thắng và độ lợi gain.\n"
        "• Kết quả thực nghiệm đối chứng sơ bộ trên DataSense IIoT 2025 (kết quả trích xuất từ results/base_datasense_s42/):"
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
        ["All Features (Gốc)", "71", "0.0%", "0.9682", "0.9745", "0.745s"],
        ["Boruta-Lite (k=25)", "25", "64.8%", "0.9675", "0.9740", "0.741s"],
        ["LGBM Importance (k=25)", "25", "64.8%", "0.9674", "0.9707", "0.725s"],
        ["Random (k=25, 20 runs)", "25", "64.8%", "0.9412", "0.9521 ± 0.012", "0.730s"],
        ["NSGA-II Knee (Sơ bộ)", "25", "64.8%", "0.9646", "0.9700", "0.246s*"]
    ]
    for r_idx, row in enumerate(rows_data):
        cells = table.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=80, right=80)
            if c_idx in [1, 2, 3, 4, 5]:
                cells[c_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    p_tbl_note = doc.add_paragraph()
    r_tn = p_tbl_note.add_run("(* Ghi chú: Thời gian suy luận của NSGA-II sơ bộ đo trên 2.000 mẫu; các baseline đo trên toàn bộ 5.817 mẫu Test)")
    r_tn.font.size = Pt(10)
    r_tn.font.italic = True

    # Sub-item 3
    p_s2_3 = doc.add_paragraph()
    p_s2_3.paragraph_format.space_before = Pt(6)
    r_s2_3 = p_s2_3.add_run("3. Thiết Lập Môi Trường Biên và Kịch Bản Benchmark Chuẩn Hóa (Nhật phụ trách):")
    r_s2_3.bold = True
    p_s2_3_c = doc.add_paragraph()
    p_s2_3_c.add_run(
        "• Khắc phục rào cản Docker: Do việc cấp quyền daemon Docker trên máy phát triển cá nhân gặp xung đột phân quyền, thành viên Nhật đã xây dựng giải pháp thay thế hoàn toàn độc lập scripts/benchmark_edge.py sử dụng trực tiếp các giao diện chuẩn của nhân Linux:\n"
        "  + Giả lập cấu hình E1 (1 vCPU, 512MB RAM): Khóa tiến trình vào duy nhất 1 nhân CPU bằng os.sched_setaffinity(pid, {0}) tương đương taskset -c 0.\n"
        "  + Giả lập cấu hình E2 (2 vCPU, 1GB RAM): Khóa tiến trình vào 2 nhân CPU bằng os.sched_setaffinity(pid, {0, 1}) tương đương taskset -c 0,1.\n"
        "  + Giám sát bộ nhớ: Sử dụng thư viện tracemalloc để đo chính xác dung lượng RAM đỉnh (peak RAM) trong quá trình nạp mô hình và suy luận.\n"
        "• Quy trình đo lường chuẩn hóa theo đề cương v6:\n"
        "  + Giai đoạn Warm-up: Thực hiện 10 lần suy luận khởi động để nạp các trang nhớ và cache CPU.\n"
        "  + Giai đoạn Đo lường: Thực hiện 30 lần lặp độc lập, lấy giá trị trung vị (median) và độ lệch chuẩn (std).\n"
        "  + Hai chế độ suy luận: Streaming theo từng gói tin (batch size = 1) và Xử lý lưu lượng lớn (batch size = 1024).\n"
        "• Kết quả đo lường thử nghiệm thực tế trên môi trường biên (trên bộ dữ liệu DataSense 10s):"
    )

    # Add Table of Edge Benchmark
    table2 = doc.add_table(rows=5, cols=6)
    table2.style = 'Table Grid'
    headers2 = ["Cấu hình biên", "Số nhân CPU", "Chế độ (Batch size)", "Độ trễ trung vị (ms)", "Độ lệch chuẩn (ms)", "RAM đỉnh (Peak)"]
    hdr_cells2 = table2.rows[0].cells
    for i, h in enumerate(headers2):
        hdr_cells2[i].text = h
        hdr_cells2[i].paragraphs[0].runs[0].bold = True
        hdr_cells2[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_margins(hdr_cells2[i], top=80, bottom=80, left=100, right=100)

    rows_data2 = [
        ["E1 (1 vCPU)", "1 nhân (core 0)", "Batch 1 (Streaming)", "1.833 ms", "± 0.449 ms", "8.2 KB"],
        ["E1 (1 vCPU)", "1 nhân (core 0)", "Batch 1024 (Lưu lượng)", "174.686 ms", "± 6.964 ms", "84.9 KB"],
        ["E2 (2 vCPU)", "2 nhân (core 0, 1)", "Batch 1 (Streaming)", "3.019 ms", "± 0.790 ms", "8.2 KB"],
        ["E2 (2 vCPU)", "2 nhân (core 0, 1)", "Batch 1024 (Lưu lượng)", "97.325 ms", "± 18.128 ms", "84.9 KB"]
    ]
    for r_idx, row in enumerate(rows_data2):
        cells = table2.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row):
            cells[c_idx].text = val
            set_cell_margins(cells[c_idx], top=60, bottom=60, left=80, right=80)
            if c_idx in [1, 2, 3, 4, 5]:
                cells[c_idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT

    # Sub-item 4
    p_s2_4 = doc.add_paragraph()
    p_s2_4.paragraph_format.space_before = Pt(6)
    r_s2_4 = p_s2_4.add_run("4. Sự Cố Phần Cứng và Công Tác Đảm Bảo An Toàn Dữ Liệu:")
    r_s2_4.bold = True
    p_s2_4_c = doc.add_paragraph()
    p_s2_4_c.add_run(
        "• Trong quá trình làm việc, ổ đĩa cứng phụ (HDD) lưu trữ mã nguồn của nhóm xuất hiện hiện tượng bad sector và lỗi truy xuất phần cứng cần phải sao lưu và cài đặt lại.\n"
        "• Nhóm đã xử lý nhanh chóng và an toàn tuyệt đối:\n"
        "  + Di chuyển toàn bộ dữ liệu sạch, mã nguồn đã vá, báo cáo và kết quả thực nghiệm sang phân vùng SSD an toàn của hệ điều hành (/home/danh/dacn/).\n"
        "  + Tạo 2 gói lưu trữ độc lập dacn_backup_20261030.tar.gz và dacn_backup_20261030.zip (7.4 MB) đã kiểm định toàn vẹn.\n"
        "  + Dọn dẹp Git repository, loại bỏ 836MB tệp rác tạm thời và loại trừ dữ liệu thô >16GB trong .gitignore, commit toàn bộ 43 tệp tin dự án vào nhánh main để sẵn sàng đồng bộ lên GitHub (https://github.com/danhnee/DACN.git)."
    )

    # Section III
    p_s3 = doc.add_paragraph()
    p_s3.paragraph_format.space_before = Pt(10)
    r_s3 = p_s3.add_run("III. ĐÁNH GIÁ MỨC ĐỘ HOÀN THÀNH TIẾN ĐỘ TUẦN 3")
    r_s3.bold = True
    r_s3.font.size = Pt(13)

    p_s3_body = doc.add_paragraph()
    p_s3_body.add_run(
        "• Đánh giá chung: Hoàn thành 100% mục tiêu của Tuần 3 theo đúng đề cương chi tiết.\n"
        "• Hệ thống mã nguồn đã được module hóa chặt chẽ (common.py), quy trình đánh giá 150 cây được thống nhất giữa NSGA-II và các Baseline.\n"
        "• Đã có đầy đủ kết quả baseline thực nghiệm để làm căn cứ đối sánh khoa học cho thuật toán NSGA-II.\n"
        "• Môi trường biên E1 và E2 đã được kiểm chứng hoạt động ổn định và đo đạc chuẩn xác qua script benchmark độc lập.\n"
        "• An toàn dữ liệu được đảm bảo an toàn tuyệt đối trước sự cố phần cứng ổ đĩa."
    )

    # Section IV
    p_s4 = doc.add_paragraph()
    p_s4.paragraph_format.space_before = Pt(10)
    r_s4 = p_s4.add_run("IV. CÁC VẤN ĐỀ TỒN ĐỌNG VÀ GIẢI PHÁP")
    r_s4.bold = True
    r_s4.font.size = Pt(13)

    p_s4_body = doc.add_paragraph()
    p_s4_body.add_run(
        "1. Vấn đề nhiễu thời gian thực khi đo hàm mục tiêu f3: Thời gian suy luận t_pred trong hàm fitness phụ thuộc vào tải CPU nền của hệ điều hành, dẫn đến việc giữa các lần chạy với cùng một seed có thể có sự biến thiên nhẹ về thứ hạng cá thể.\n"
        "   -> Giải pháp: Nhóm khẳng định trong báo cáo đồ án rằng tính tái lập được bảo đảm ở mức thống kê (statistical reproducibility). Nhóm sẽ chạy chính thức trên 5 seed ngẫu nhiên độc lập (seed 42, 43, 44, 45, 46) và lưu trữ đầy đủ pareto_F, pareto_X cho từng seed để phân tích phân phối độ lệch chuẩn.\n"
        "2. Vấn đề tương quan độ phẳng của f3 theo số đặc trưng k: Do số cây cố định 60 khi tính fitness, thời gian suy luận phụ thuộc nhiều vào độ sâu cây và cấu trúc phân nhánh hơn là số đặc trưng. Nhóm sẽ ghi nhận chi tiết hiện tượng này và phân tích hệ số tương quan Pearson trong nội dung báo cáo nghiên cứu ở Tuần 4."
    )

    # Section V
    p_s5 = doc.add_paragraph()
    p_s5.paragraph_format.space_before = Pt(10)
    r_s5 = p_s5.add_run("V. KẾ HOẠCH CÔNG VIỆC TRONG TUẦN 4")
    r_s5.bold = True
    r_s5.font.size = Pt(13)

    p_s5_body = doc.add_paragraph()
    p_s5_body.add_run(
        "Bước sang giai đoạn chạy thực nghiệm toàn diện và phân tích sâu kết quả, nhóm đề ra kế hoạch tuần 4 như sau:\n"
        "• Thành viên Danh: Tiến hành chạy chính thức NSGA-II trên 5 seed độc lập cho bộ dữ liệu DataSense IIoT 2025; thu thập tập nghiệm Pareto Front và trích xuất các nghiệm tiêu biểu (Knee, delta-tolerance 1%, 2%).\n"
        "• Thành viên Nam: Triển khai chạy NSGA-II và Baselines trên bộ dữ liệu mạng NetFlow NF-UQ-NIDS-v2 (167.820 mẫu); lập trình script vẽ biểu đồ phân tán Pareto đa mục tiêu và biểu đồ hộp (boxplot) so sánh phân phối Macro-F1.\n"
        "• Thành viên Nhật: Áp dụng script scripts/benchmark_edge.py để đo kiểm toàn diện độ trễ và bộ nhớ RAM của các nghiệm chọn lọc trên môi trường E1 và E2; tổng hợp số liệu cho Bảng kết quả so sánh trong báo cáo Tuần 4."
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

    output_path = "/home/danh/dacn/BaoCao_Tuan3_Nhom9.docx"
    doc.save(output_path)
    print(f"Report generated successfully at: {output_path}")

    # Copy to /home/danh and Downloads
    shutil.copy(output_path, "/home/danh/BaoCao_Tuan3_Nhom9.docx")
    shutil.copy(output_path, "/home/danh/Downloads/BaoCao_Tuan3_Nhom9.docx")
    try:
        shutil.copy(output_path, "/mnt/9698C2DB98C2B94F/dacn/BaoCao_Tuan3_Nhom9.docx")
    except Exception as e:
        print("Note: /mnt drive copy skipped or not mounted.")
    print("Copied to /home/danh/ and /home/danh/Downloads/ successfully.")

if __name__ == "__main__":
    create_report()
