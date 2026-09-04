import streamlit as st
import time
from google import genai
from google.genai import types
from PIL import Image

# Cấu hình trang Web
st.set_page_config(page_title="AI Đồng Hành Tự Chủ", page_icon="🤖")
st.title("🤖 Trợ Lý AI Đồng Hành Tự Chủ")
st.caption("Hệ thống hỗ trợ học sinh THCS phát triển năng lực tự học")

SYSTEM_PROMPT = """
VAI TRÒ
Bạn là “AI Đồng hành Tự chủ” – một trợ lý học tập dành cho học sinh THCS. Mục tiêu chính của bạn không phải là đưa ra đáp án nhanh nhất, mà là hỗ trợ học sinh tự suy nghĩ, tự đưa ra quyết định, tự kiểm tra và tự giải quyết vấn đề.

NGUYÊN TẮC CỐT LÕI
1. Không làm bài thay học sinh khi học sinh chưa tự suy nghĩ.
2. Không đưa đáp án trực tiếp ngay khi học sinh vừa đặt câu hỏi hoặc gửi ảnh đề bài.
3. Luôn khuyến khích học sinh trình bày suy nghĩ, cách làm hoặc dự đoán của mình trước.
4. Ưu tiên đặt câu hỏi gợi mở dựa trên nội dung ảnh/câu hỏi.
5. Chỉ tăng mức độ hỗ trợ khi học sinh thực sự gặp khó khăn.

PHONG CÁCH GIAO TIẾP
Thân thiện, tích cực, phù hợp với học sinh THCS, không phán xét.
"""

# Khởi tạo Client
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

# Khởi tạo lịch sử
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_contents" not in st.session_state:
    st.session_state.api_contents = []

# Hiển thị lịch sử tin nhắn
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if "image" in message:
            st.image(message["image"], use_container_width=True)
        if "content" in message and message["content"]:
            st.markdown(message["content"])

# Nút tải ảnh lên ở thanh bên hoặc giao diện chính
uploaded_file = st.file_uploader("Tải ảnh đề bài/bài làm (nếu có):", type=["png", "jpg", "jpeg"])

# Nhập tin nhắn và xử lý
if prompt := st.chat_input("Nhập câu hỏi hoặc câu trả lời của em ở đây..."):
    # Chuẩn bị tin nhắn người dùng
    user_msg = {"role": "user", "content": prompt}
    api_parts = [{"text": prompt}]
    
    # Mở ảnh nếu học sinh có tải lên
    img = None
    if uploaded_file is not None:
        img = Image.open(uploaded_file)
        user_msg["image"] = img
        api_parts.append(img)  # Truyền trực tiếp đối tượng PIL Image vào SDK

    # Hiển thị tin nhắn người dùng
    with st.chat_message("user"):
        if img:
            st.image(img, use_container_width=True)
        st.markdown(prompt)

    st.session_state.messages.append(user_msg)
    st.session_state.api_contents.append({
        "role": "user",
        "parts": api_parts
    })

    # Gọi API AI
    with st.chat_message("assistant"):
        with st.spinner("AI đang xem hình và suy nghĩ..."):
            response = None
            max_retries = 3
            
            for attempt in range(max_retries):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=st.session_state.api_contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.3
                        )
                    )
                    break
                except Exception as e:
                    if "503" in str(e) or "UNAVAILABLE" in str(e):
                        if attempt < max_retries - 1:
                            time.sleep(2)
                            continue
                    st.error(f"Lỗi kết nối API: {e}")
                    break
            
            if response:
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.session_state.api_contents.append({
                    "role": "model",
                    "parts": [{"text": response.text}]
                })
