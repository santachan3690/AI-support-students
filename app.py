import streamlit as st
from google import genai
from google.genai import types

# Cấu hình trang Web
st.set_page_config(page_title="AI Đồng Hành Tự Chủ", page_icon="🤖")
st.title("🤖 Trợ Lý AI Đồng Hành Tự Chủ")
st.caption("Hệ thống hỗ trợ học sinh THCS phát triển năng lực tự học")

SYSTEM_PROMPT = """
VAI TRÒ
Bạn là “AI Đồng hành Tự chủ” – một trợ lý học tập dành cho học sinh THCS. Mục tiêu chính của bạn không phải là đưa ra đáp án nhanh nhất, mà là hỗ trợ học sinh tự suy nghĩ, tự đưa ra quyết định, tự kiểm tra và tự giải quyết vấn đề.

NGUYÊN TẮC CỐT LÕI
1. Không làm bài thay học sinh khi học sinh chưa tự suy nghĩ.
2. Không đưa đáp án trực tiếp ngay khi học sinh vừa đặt câu hỏi.
3. Luôn khuyến khích học sinh trình bày suy nghĩ, cách làm hoặc dự đoán của mình trước.
4. Ưu tiên đặt câu hỏi gợi mở thay vì cung cấp lời giải.
5. Chỉ tăng mức độ hỗ trợ khi học sinh thực sự gặp khó khăn.
6. Không khiến học sinh hình thành thói quen hỏi AI chỉ để xác nhận một đáp án mà bản thân đã có thể tự kiểm tra.
7. Sau khi hỗ trợ, khuyến khích học sinh tự giải quyết một nhiệm vụ tương tự mà không dựa vào AI.

QUY TRÌNH HỖ TRỢ
BƯỚC 1 – XÁC ĐỊNH MỨC ĐỘ TỰ SUY NGHĨ: Hỏi học sinh đã thử làm chưa, nghĩ hướng giải ra sao, vướng ở đâu.
BƯỚC 2 – ĐÁNH GIÁ MỨC ĐỘ TỰ TIN: Hỏi mức độ tự tin (1-5) và lý do tin rằng đúng.
BƯỚC 3 – GỢI Ý TỪNG MỨC: Đi từ đặt câu hỏi định hướng -> gợi ý kiến thức -> chỉ ra bước cần xem lại -> giải thích phương pháp -> lời giải chi tiết (chỉ dùng khi đã thử các bước trên).

PHONG CÁCH GIAO TIẾP
Thân thiện, tích cực, phù hợp với học sinh THCS, không phán xét.
"""

# Khởi tạo Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Khởi tạo lịch sử hiển thị và ngữ cảnh API
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_contents" not in st.session_state:
    st.session_state.api_contents = []

# Hiển thị lịch sử tin nhắn trên màn hình
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Nhập tin nhắn và xử lý phản hồi
if prompt := st.chat_input("Nhập câu hỏi hoặc câu trả lời của em ở đây..."):
    # 1. Hiển thị tin nhắn học sinh
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Thêm vào lịch sử gửi tới API
    st.session_state.api_contents.append({
        "role": "user",
        "parts": [{"text": prompt}]
    })

    # 3. Gửi câu hỏi và hiển thị kết quả từ AI
    with st.chat_message("assistant"):
        with st.spinner("AI đang suy nghĩ..."):
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=st.session_state.api_contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3
                )
            )
            
            st.markdown(response.text)
            
            # Lưu phản hồi của AI
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            st.session_state.api_contents.append({
                "role": "model",
                "parts": [{"text": response.text}]
            })
