import random
import requests
import streamlit as st
from utils.data_manager import load_data

st.set_page_config(page_title="AI Reading Assistant - Vocabulary Trainer", page_icon="🤖", layout="wide")

st.title("🤖 AI Reading Assistant")
st.caption("Tạo bài đọc hiểu / đoạn văn thực hành từ chính các từ vựng bạn đã thuộc!")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# --- 1. NHẬP GEMINI API KEY ---
st.write("📌 **Cấu hình Gemini AI:**")
api_key = st.text_input("Nhập Gemini API Key của bạn (chỉ cần nhập 1 lần):", type="password", key="gemini_api_key")

if not api_key:
    st.info("💡 Bạn chưa có API Key? Hãy lấy miễn phí tại: https://aistudio.google.com/")
    st.stop()

clean_api_key = api_key.strip()

# --- 2. ĐỌC TỪ VỰNG CÁ NHÂN ---
colloc_data = load_data(f"data_collocation_{username}.json")
vocab_data = load_data(f"data_vocab_{username}.json")

user_all_words = list({**colloc_data, **vocab_data}.keys())

if len(user_all_words) < 5:
    st.warning("⚠️ Bạn cần có ít nhất 5 từ vựng trong kho cá nhân để AI tạo bài đọc. Hãy sang mục **Library** để thêm từ trước nhé!")
    st.stop()

st.divider()

# --- 3. CHỌN SỐ LƯỢNG TỪ VÀ TẠO BÀI ĐỌC ---
st.subheader("🎯 Thiết lập bài tập AI")

col_num, col_type = st.columns([1, 2])

with col_num:
    num_words = st.slider("Số lượng từ vựng muốn đưa vào bài:", min_value=5, max_value=min(15, len(user_all_words)), value=min(10, len(user_all_words)))

with col_type:
    task_type = st.selectbox(
        "Chọn dạng bài tập bạn muốn luyện:",
        [
            "📝 Đoạn văn luyện dịch (Anh -> Việt) kèm chú thích từ",
            "📖 Bài đọc hiểu Tiếng Anh + 3 câu hỏi trắc nghiệm",
            "💬 Đoạn hội thoại thực tế giữa 2 người"
        ]
    )

if st.button("🚀 AI Tạo Bài Tập Ngay", type="primary", use_container_width=True):
    # Chọn ngẫu nhiên N từ trong kho của user
    selected_words = random.sample(user_all_words, num_words)
    words_str = ", ".join([f"'{w}'" for w in selected_words])
    
    st.write("📌 **Các từ vựng được chọn cho bài này:**")
    st.info(words_str)
    
    # Soạn Prompt gửi cho Gemini AI
    prompt_text = f"""
    Bạn là một giáo viên tiếng Anh giỏi. Hãy viết một bài tập giúp tôi luyện tập dựa trên danh sách từ/cụm từ sau: [{words_str}].

    Yêu cầu:
    1. Yêu cầu tạo dạng bài: {task_type}.
    2. Trong đoạn văn tiếng Anh, hãy BÔI ĐEN (**bold**) đúng các từ trong danh sách trên mỗi khi chúng xuất hiện.
    3. Đảm bảo ngữ cảnh tự nhiên, mạch lạc và chuẩn ngữ pháp.
    4. Cuối bài, hãy cung cấp danh sách từ vựng đã dùng kèm nghĩa tiếng Việt ngắn gọn.
    """

    with st.spinner("🤖 AI đang suy nghĩ và tạo bài viết cho bạn..."):
        # Thử danh sách các model chuẩn nhất của Gemini
        models_to_try = [
            "gemini-1.5-flash",
            "gemini-2.5-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]

        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }

        success = False
        last_error = ""

        # Lặp qua từng tên model để gọi API
        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={clean_api_key}"
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=30)
                res_data = res.json()

                if res.status_code == 200:
                    result_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    st.write("---")
                    st.markdown(result_text)
                    st.balloons()
                    success = True
                    break
                else:
                    last_error = res_data.get("error", {}).get("message", res.text)
            except Exception as e:
                last_error = str(e)
                continue

        if not success:
            st.error(f"❌ Có lỗi kết nối AI: {last_error}")
