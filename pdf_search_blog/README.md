# Công cụ thao tác với PDF - Blog

## 1. Công cụ PDF Online

### 1.1. iLovePDF (https://www.ilovepdf.com/)
- **Chức năng chính:**
  - Chuyển đổi PDF sang Word, Excel, PowerPoint
  - Nén/Giảm dung lượng PDF
  - Ghép/Tách file PDF
  - Thêm số trang, chữ ký, watermark
  - Bảo vệ PDF bằng mật khẩu
- **Ưu điểm:**
  - Miễn phí
  - Giao diện đơn giản, dễ sử dụng
- **Nhược điểm:**
  - Giới hạn dung lượng file - (có thể chia nhỏ file ra thành nhiều phần)
  - Mất khá nhiều thời gian

### 1.2. SmallPDF (https://smallpdf.com/) - 
- **Tính năng:** Tương tự iLovePDF nhưng ổn hơn
- **Giao diện:** Chuyên nghiệp hơn
- **Phiên bản:** Có phiên bản trả phí với nhiều tính năng nâng cao



## 2. Adobe Acrobat Reader DC - Phần mềm cài đặt trên máy tính

Hướng dẫn cài đặt:
---
- Truy cập vào trang chủ *Adobe Acrobat Reader* tải xuống phiên bản mới nhất [Adobe Arcobat Reader](https://www.adobe.com/vn_en/acrobat/pdf-reader.html)
- Làm theo hướng dẫn sử dụng [Hướng dẫn cách cài đặt và sử dụng Adobe Arcobat](https://www.thegioididong.com/game-app/cach-tai-va-su-dung-adobe-reader-ve-may-tinh-xem-doc-file-pdf-1292825)

### 2.1. Các tính năng cơ bản (Miễn phí)
- Đọc và xem PDF
- Thêm comment, highlight
- Ký tên điện tử cơ bản
- Tìm kiếm văn bản
- Cung cấp 10 Credit AI/mỗi tài khoản nâng cao cho phép tìm ngữ liệu thông tin với độ chính xác (tương đương) cao. *AI Chat With PDF*

### 2.3. Hướng dẫn sử dụng cơ bản
Thông tin các phím tắt cơ bản [Các phím tắt cơ bản thao tác trên Adobe Arcobat](https://www.thegioididong.com/game-app/tong-hop-phim-tat-trong-adobe-acrobat-reader-nhanh-tien-loi-1370602)



## 4. Phân tích mã nguồn `search.py` - Áp dụng xử lý dữ liệu + AI Gemini (Code tham khảo)

### 4.1. Tổng quan
Mã nguồn `search.py` được thiết kế để xử lý và phân tích nội dung từ tài liệu PDF, sử dụng các thư viện như `fitz` để trích xuất văn bản và `google.generativeai` để phân tích nội dung.

### 4.2. Các chức năng chính

1. **`clean_text(text)`**:
   - **Chức năng:** Làm sạch văn bản bằng cách loại bỏ ký tự đặc biệt và chuẩn hóa khoảng trắng.
   - **Chi tiết:** Sử dụng biểu thức chính quy để loại bỏ các ký tự không mong muốn và chuẩn hóa khoảng trắng giữa các từ.

2. **`split_into_semantic_chunks(text, max_chunk_size=500)`**:
   - **Chức năng:** Chia văn bản thành các đoạn nhỏ hơn (chunks) để xử lý dễ dàng hơn.
   - **Chi tiết:** Sử dụng thư viện `underthesea` để tách câu và kiểm tra kích thước của từng đoạn để đảm bảo không vượt quá kích thước tối đa.

3. **`analyze_chunk_content(chunk, query, model, max_retries=3)`**:
   - **Chức năng:** Phân tích nội dung của từng đoạn văn và so sánh với truy vấn.
   - **Chi tiết:** Tạo một prompt cho mô hình AI để đánh giá mức độ liên quan của đoạn văn với truy vấn, và thực hiện thử lại nếu có lỗi xảy ra.

4. **`extract_text_by_page_with_ai(pdf_path, query, relevance_threshold=7, call_limit=10, cooldown=10)`**:
   - **Chức năng:** Trích xuất văn bản từ từng trang của tài liệu PDF và phân tích nội dung.
   - **Chi tiết:** Mở tài liệu PDF, trích xuất văn bản từ từng trang, làm sạch văn bản và phân tích nội dung để tìm các trang có độ liên quan cao với truy vấn.

5. **`main()`**:
   - **Chức năng:** Điểm khởi đầu của chương trình.
   - **Chi tiết:** Xác định đường dẫn PDF và truy vấn để phân tích, sau đó gọi hàm `extract_text_by_page_with_ai` để thực hiện phân tích.

___
