import fitz  
import re
from tqdm import tqdm
import google.generativeai as genai
import time

genai.configure(api_key="AIzaSyD46cIWhQVNm9YJ7sfmxuyFaPwrgEAZaHc")

def extract_text_by_page_with_ai(pdf_path, query, relevance_threshold=7, call_limit=14, cooldown=5):
    doc = fitz.open(pdf_path)
    matched_pages = []
    
    def semantic_similarity_check(page_num, page_text):
        prompt = f"""
        Đánh giá mức độ liên quan giữa đoạn văn sau và truy vấn bằng tiếng Việt.
        Trả về điểm số từ 0 đến 10, trong đó 0 là hoàn toàn không liên quan và 10 là rất liên quan.
        Chỉ trả về số điểm, không giải thích.

        Truy vấn: {query}

        Đoạn văn: {page_text}
        """
        model = genai.GenerativeModel('gemini-pro')
        try:
            response = model.generate_content(prompt)
            score = float(response.text.strip())
            return page_num, score
        except Exception as e:
            print(f"Lỗi xử lý AI trên trang {page_num}: {e}")
            return page_num, 0

    call_count = 0  

   
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text")
        
       
        page_num, score = semantic_similarity_check(page_num + 1, page_text)
        
        
        if score >= relevance_threshold:
            matched_pages.append((page_num, page.get_text("text")))

       
        call_count += 1
        if call_count >= call_limit:
            print(f"Đã đạt giới hạn {call_limit} lần gọi API, đang tạm nghỉ trong {cooldown} giây...")
            time.sleep(cooldown)
            call_count = 0  

    doc.close()
    return matched_pages

def main():
    pdf_path = r"C:\Users\ACER\Downloads\search\chuong1.pdf" 
    query = """
    Hình thức tổ chức nhà cửa chủ yếu của người Việt vùng Tây Nam Bộ là phân bố theo dạng tuyến hình xương cá (hay tỏa tia): 
    nhà cửa nhìn ra sông, lấy sông làm mặt tiền, khiến cho làng mạc Tây Nam Bộ có bộ mặt khác hẳn nông thôn miền Trung, miền Bắc. 
    Hình thức cư trú như vậy là một sự thích nghi hữu hiệu với môi trường thiên nhiên sông nước, chằng chịt kênh rạch
    """
    
    print("Đang kiểm tra từng trang của PDF để tìm nội dung tương đồng về ngữ nghĩa...")
    matched_pages = extract_text_by_page_with_ai(pdf_path, query)

    print("\nKết quả tìm kiếm:")
    for page_num, content in matched_pages:
        print(f"\n--- Trang {page_num} ---")
        print(content)
        print("-" * 50)

    print(f"\nTổng số trang có nội dung tương đồng: {len(matched_pages)}")

if __name__ == "__main__":
    main()
