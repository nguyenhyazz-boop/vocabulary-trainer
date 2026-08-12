import random
import requests
import streamlit as st
from utils.data_manager import load_data

st.set_page_config(page_title="AI Reading Assistant - Vocabulary Trainer", page_icon="🤖", layout="wide")

st.title("🤖 AI Reading Assistant")
st.caption("Tùy chọn danh sách từ vựng cá nhân để AI tạo bài đọc & bài tập thực hành!")

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

if not user_all_words:
    st.warning("⚠️ Kho từ vựng cá nhân của bạn hiện đang trống. Hãy sang mục **Library** để chọn thêm từ trước nhé!")
    st.stop()

st.divider()

# --- 3. TÙY CHỌN CHỌN TỪ VỰNG CỤ THỂ ---
st.subheader("🎯 Chọn danh sách từ vựng muốn đưa vào bài")

# Chọn danh sách từ bằng Multiselect
selected_words = st.multiselect(
    "Tích chọn các từ/cụm từ bạn muốn luyện tập:",
    options=user_all_words,
    default=user_all_words[:min(8, len(user_all_words))]
)

# Nút tiện ích hỗ trợ chọn nhanh
col_quick1, col_quick2 = st.columns(2)
with col_quick1:
    if st.button("🎲 AI chọn ngẫu nhiên 5 từ cho tôi", use_container_width=True):
        st.session_state.selected_words_override = random.sample(user_all_words, min(5, len(user_all_words)))
        st.rerun()

with col_quick2:
    if st.button("🎲 AI chọn ngẫu nhiên 10 từ cho tôi", use_container_width=True):
        st.session_state.selected_words_override = random.sample(user_all_words, min(10, len(user_all_words)))
        st.rerun()

if "selected_words_override" in st.session_state:
    selected_words = st.session_state.selected_words_override
    del st.session_state.selected_words_override

st.write("")
task_type = st.selectbox(
    "Chọn dạng bài tập bạn muốn luyện:",
    [
        "📝 Đoạn văn luyện dịch (Anh -> Việt) kèm chú thích từ",
        "📖 Bài đọc hiểu Tiếng Anh + 3 câu hỏi trắc nghiệm",
        "💬 Đoạn hội thoại thực tế giữa 2 người"
    ]
)

st.divider()

# --- 4. GỬI YÊU CẦU CHO GEMINI AI VÀ GIỮ LẠI KẾT QUẢ ---
if st.button("🚀 AI Tạo Bài Tập Ngay", type="primary", use_container_width=True):
    if not selected_words:
        st.warning("⚠️ Bạn chưa chọn từ vựng nào cả! Hãy chọn ít nhất 1 từ ở danh sách phía trên.")
        st.stop()

    words_str = ", ".join([f"'{w}'" for w in selected_words])

    prompt_text = f"""
    Bạn là một giáo viên tiếng Anh giỏi. Hãy viết một bài tập giúp tôi luyện tập dựa trên danh sách từ/cụm từ sau: [{words_str}].

    Yêu cầu:
    1. Yêu cầu tạo dạng bài: {task_type}.
    2. Trong đoạn văn tiếng Anh, hãy BÔI ĐEN (**bold**) đúng các từ trong danh sách trên mỗi khi chúng xuất hiện.
    3. Đảm bảo ngữ cảnh tự nhiên, mạch lạc và chuẩn ngữ pháp.
    4. Cuối bài, hãy cung cấp danh sách từ vựng đã dùng kèm nghĩa tiếng Việt ngắn gọn.
    """

    with st.spinner("🤖 Đang kết nối Gemini AI để tạo bài tập cho các từ bạn đã chọn..."):
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{
                "parts": [{"text": prompt_text}]
            }]
        }

        # Quét danh sách Model đang hỗ trợ
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={clean_api_key}"
        working_models = []
        
        try:
            list_res = requests.get(list_url, timeout=10)
            if list_res.status_code == 200:
                models_info = list_res.json().get("models", [])
                for m in models_info:
                    methods = m.get("supportedGenerationMethods", [])
                    if "generateContent" in methods:
                        name = m.get("name", "").replace("models/", "")
                        working_models.append(name)
        except Exception:
            pass

        if not working_models:
            working_models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]

        success = False
        last_error = ""

        for model_name in working_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={clean_api_key}"
            try:
                res = requests.post(url, json=payload, headers=headers, timeout=30)
                res_data = res.json()

                if res.status_code == 200:
                    result_text = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    
                    # LƯU KẾT QUẢ VÀO SESSION STATE ĐỂ KHÔNG BỊ MẤT KHI CHUYỂN TRANG
                    st.session_state.ai_saved_reading = {
                        "text": result_text,
                        "words": selected_words
                    }
                    success = True
                    st.balloons()
                    break
                else:
                    last_error = res_data.get("error", {}).get("message", res.text)
            except Exception as e:
                last_error = str(e)
                continue

        if not success:
            st.error(f"❌ Có lỗi kết nối AI: {last_error}")

# --- 5. HIỂN THỊ BÀI ĐỌC ĐÃ LƯU (KỂ CẢ KHI CHUYỂN TRANG QUAY LẠI) ---
if "ai_saved_reading" in st.session_state:
    saved_data = st.session_state.ai_saved_reading
    st.write("---")
    st.write(f"📌 **{len(saved_data['words'])} từ vựng trong bài đọc này:**")
    st.info(", ".join([f"'{w}'" for w in saved_data['words']]))
    st.markdown(saved_data["text"])
