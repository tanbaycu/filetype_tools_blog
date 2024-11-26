import fitz  
import re
from tqdm import tqdm
import google.generativeai as genai
import time
from underthesea import sent_tokenize

genai.configure(api_key="AIzaSyD46cIWhQVNm9YJ7sfmxuyFaPwrgEAZaHc")

def clean_text(text):
    # Loại bỏ ký tự đặc biệt và chuẩn hóa khoảng trắng
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s\.,;:!?\u00C0-\u1EF9\(\)\[\]\"\']+', '', text)
    text = re.sub(r'\s*([.,;:!?])', r'\1', text)
    return text.strip()

def split_into_semantic_chunks(text, max_chunk_size=500):
    # Giảm kích thước chunk để xử lý chi tiết hơn
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

def analyze_chunk_content(chunk, query, model, max_retries=3):
    # Phân tích chi tiết từng đoạn văn với cơ chế thử lại
    prompt = f"""
    Hãy phân tích kỹ lưỡng và so sánh chi tiết nội dung giữa đoạn văn và truy vấn sau.
    Đánh giá mức độ liên quan dựa trên:
    1. Sự trùng khớp về chủ đề chính
    2. Sự tương đồng về ngữ cảnh
    3. Mức độ chi tiết phù hợp
    4. Tính liên quan của thông tin
    
    Chấm điểm từ 0-10, trong đó:
    - 0-2: Hoàn toàn không liên quan
    - 3-4: Có rất ít điểm chung
    - 5-6: Có một số điểm tương đồng
    - 7-8: Liên quan đáng kể
    - 9-10: Rất liên quan, trùng khớp cao
    
    Chỉ trả về số điểm, không giải thích.

    Truy vấn: {query}
    Đoạn văn: {chunk}
    """
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(prompt)
            return float(response.text.strip())
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Lỗi lần {attempt + 1}, thử lại sau 5 giây: {e}")
                time.sleep(5)
            else:
                print(f"Lỗi sau {max_retries} lần thử: {e}")
                return 0

def extract_text_by_page_with_ai(pdf_path, query, relevance_threshold=7, call_limit=10, cooldown=10):
    doc = fitz.open(pdf_path)
    matched_pages = []
    model = genai.GenerativeModel('gemini-pro')
    call_count = 0
    
    print("\nBắt đầu phân tích tài liệu PDF...")
    
    for page_num in tqdm(range(len(doc)), desc="Đang xử lý các trang"):
        page_start_time = time.time()
        page = doc[page_num]
        
        # Trích xuất văn bản với các tùy chọn nâng cao để tối ưu cho tiếng Việt
        try:
            page_text = page.get_text(
                "text", 
                sort=True,
                flags=fitz.TEXT_PRESERVE_LIGATURES | 
                      fitz.TEXT_PRESERVE_WHITESPACE |
                      fitz.TEXT_PRESERVE_IMAGES |
                      fitz.TEXT_DEHYPHENATE |
                      fitz.TEXT_PRESERVE_SPANS |
                      fitz.TEXT_MEDIABOX_CLIP
            )
            
            # Thử trích xuất lại với phương pháp khác nếu kết quả rỗng
            if not page_text.strip():
                page_text = page.get_text(
                    "blocks",
                    sort=True,
                    flags=fitz.TEXT_PRESERVE_LIGATURES |
                          fitz.TEXT_PRESERVE_WHITESPACE
                )
                page_text = " ".join([block[4] for block in page_text])
            
            cleaned_text = clean_text(page_text)
            
            # Kiểm tra và đảm bảo văn bản có nội dung
            if not cleaned_text.strip():
                print(f"Cảnh báo: Trang {page_num + 1} không có nội dung sau khi làm sạch, thử phương pháp trích xuất khác...")
                # Thử phương pháp trích xuất cuối cùng
                page_text = page.get_text("rawdict")
                cleaned_text = clean_text(" ".join([block["text"] for block in page_text["blocks"]]))
            
            print(f"\nNội dung trang {page_num + 1}:")
            print(cleaned_text[:500] + "..." if len(cleaned_text) > 500 else cleaned_text)
            
        except Exception as e:
            print(f"Lỗi khi trích xuất trang {page_num + 1}: {e}")
            continue
            
        # Phân tích nội dung
        text_chunks = split_into_semantic_chunks(cleaned_text)
        chunk_scores = []
        
        print(f"\nĐang phân tích trang {page_num + 1}...")
        
        for chunk in text_chunks:
            score = analyze_chunk_content(chunk, query, model)
            chunk_scores.append(score)
            
            call_count += 1
            if call_count >= call_limit:
                print(f"\nĐã đạt giới hạn {call_limit} lần gọi API. Tạm nghỉ {cooldown} giây...")
                time.sleep(cooldown)
                call_count = 0
        
        # Tính điểm và lưu kết quả
        if chunk_scores:
            max_score = max(chunk_scores)
            avg_score = sum(chunk_scores) / len(chunk_scores)
            final_score = (max_score * 0.7) + (avg_score * 0.3)
            
            if final_score >= relevance_threshold:
                matched_pages.append((page_num + 1, final_score, cleaned_text))
                print(f"Trang {page_num + 1}: Điểm số {final_score:.2f}/10")
        
        page_time = time.time() - page_start_time
        print(f"Hoàn thành xử lý trang {page_num + 1} trong {page_time:.1f} giây")
    
    # Sắp xếp kết quả theo điểm số
    matched_pages.sort(key=lambda x: x[1], reverse=True)
    
    print("\nKết quả phân tích chi tiết:")
    for page_num, score, content in matched_pages:
        print(f"\n{'='*40}")
        print(f"Trang {page_num} (Độ liên quan: {score:.2f}/10)")
        print(f"{'='*40}")
        preview = content[:300] + "..." if len(content) > 300 else content
        print(preview)
        print(f"{'='*40}\n")

    return matched_pages

def main():
    pdf_path = r"C:\Users\ACER\Downloads\search\chuong1.pdf"
    query = """
    Hình thức tổ chức nhà cửa chủ yếu của người Việt vùng Tây Nam Bộ là phân bố theo dạng tuyến hình xương cá (hay tỏa tia): 
    nhà cửa nhìn ra sông, lấy sông làm mặt tiền, khiến cho làng mạc Tây Nam Bộ có bộ mặt khác hẳn nông thôn miền Trung, miền Bắc. 
    Hình thức cư trú như vậy là một sự thích nghi hữu hiệu với môi trường thiên nhiên sông nước, chằng chịt kênh rạch
    """
    
    results = extract_text_by_page_with_ai(pdf_path, query)

if __name__ == "__main__":
    main()