import random
import requests
import datetime
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="AI Reading Assistant - Vocabulary Trainer", page_icon="🤖", layout="wide")

st.title("🤖 AI Reading Assistant")
st.caption("Tạo bài đọc hiểu / luyện tập từ vựng cá nhân & lưu lịch sử tự động!")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username
history_file = f"ai_history_{username}.json"

# Đọc lịch sử bài học AI đã lưu của User
ai_history = load_data(history_file)
if not isinstance(ai_history, list):
    ai_history = []

# ĐỌC KHO TỪ VỰNG CÁ NHÂN
colloc_data = load_data(f"data_collocation_{username}.json")
vocab_data = load_data(f"data_vocab_{username}.json")
user_all_words = list({**colloc_data, **vocab_data}.keys())

# CẤU HÌNH API KEY CHUNG CHO CẢ TRANG
st.write("📌 **Cấu hình Gemini AI:**")
api_key = st.text_input("Nhập Gemini API Key của bạn (chỉ cần nhập 1 lần):", type="password", key="gemini_api_key")

if not api_key:
    st.info("💡 Bạn chưa có API Key? Hãy lấy miễn phí tại: https://aistudio.google.com/")

clean_api_key = api_key.strip() if api_key else ""

st.divider()

# Tạo 2 Tab
tab_create, tab_history = st.tabs(["🚀 Tạo bài đọc mới", "📜 Lịch sử tạo bài AI"])

# =========================================================
# TAB 1: TẠO BÀI ĐỌC MỚI
# =========================================================
with tab_create:
    if not clean_api_key:
        st.warning("⚠️ Vui lòng nhập Gemini API Key ở ô phía trên trước khi tạo bài tập mới!")
    elif not user_all_words:
        st.warning("⚠️ Kho từ vựng cá nhân của bạn hiện đang trống. Hãy sang mục **Library** để thêm từ trước nhé!")
    else:
        st.subheader("🎯 Chọn danh sách từ vựng muốn đưa vào bài")

        selected_words = st.multiselect(
            "Tích chọn các từ/cụm từ bạn muốn luyện tập:",
            options=user_all_words,
            default=user_all_words[:min(8, len(user_all_words))]
        )

        col_quick1, col_quick2 = st.columns(2)
        with col_quick1:
            if st.button("🎲 AI chọn ngẫu nhiên 5 từ", use_container_width=True):
                st.session_state.selected_words_override = random.sample(user_all_words, min(5, len(user_all_words)))
                st.rerun()

        with col_quick2:
            if st.button("🎲 AI chọn ngẫu nhiên 10 từ", use_container_width=True):
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

        if st.button("🚀 AI Tạo Bài Tập Ngay", type="primary", use_container_width=True):
            if not selected_words:
                st.warning("⚠️ Bạn chưa chọn từ vựng nào cả!")
            else:
                words_str = ", ".join([f"'{w}'" for w in selected_words])

                prompt_text = f"""
                Bạn là một giáo viên tiếng Anh giỏi. Hãy viết một bài tập giúp tôi luyện tập dựa trên danh sách từ/cụm từ sau: [{words_str}].

                Yêu cầu:
                1. Yêu cầu tạo dạng bài: {task_type}.
                2. Trong đoạn văn tiếng Anh, hãy BÔI ĐEN (**bold**) đúng các từ trong danh sách trên mỗi khi chúng xuất hiện.
                3. Đảm bảo ngữ cảnh tự nhiên, mạch lạc và chuẩn ngữ pháp.
                4. Cuối bài, hãy cung cấp danh sách từ vựng đã dùng kèm nghĩa tiếng Việt ngắn gọn.
                """

                with st.spinner("🤖 AI đang suy nghĩ và tạo bài viết cho bạn..."):
                    headers = {"Content-Type": "application/json"}
                    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

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
                                
                                new_entry = {
                                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "task_type": task_type,
                                    "words": selected_words,
                                    "content": result_text
                                }
                                
                                ai_history.insert(0, new_entry)
                                save_data(ai_history, history_file)
                                
                                success = True
                                st.balloons()
                                st.success("🎉 Đã tạo bài tập thành công và lưu vào Lịch sử!")
                                st.rerun()
                                break
                            else:
                                last_error = res_data.get("error", {}).get("message", res.text)
                        except Exception as e:
                            last_error = str(e)
                            continue

                    if not success:
                        st.error(f"❌ Có lỗi kết nối AI: {last_error}")

        if ai_history:
            latest_item = ai_history[0]
            st.write("---")
            st.subheader("📄 Bài tập vừa tạo gần nhất:")
            st.caption(f"🕒 Thời gian: {latest_item['time']} | 🎯 Dạng bài: {latest_item['task_type']}")
            st.info(f"📌 Từ vựng: {', '.join(latest_item['words'])}")
            st.markdown(latest_item["content"])


# =========================================================
# TAB 2: LỊCH SỬ TẠO BÀI AI
# =========================================================
with tab_history:
    st.subheader("📜 Danh sách bài đọc AI đã lưu")
    
    if not ai_history:
        st.info("Chưa có lịch sử bài đọc nào được lưu. Hãy tạo bài đọc mới ở Tab **Tạo bài đọc mới** nhé!")
    else:
        if st.button("🗑️ Xóa toàn bộ lịch sử bài đọc", type="secondary"):
            save_data([], history_file)
            st.success("Đã xóa sạch lịch sử!")
            st.rerun()

        st.write("---")

        for idx, item in enumerate(ai_history):
            with st.expander(f"📌 Bài #{len(ai_history) - idx} - {item['time']} ({len(item['words'])} từ)"):
                st.caption(f"**Dạng bài:** {item['task_type']}")
                st.write(f"**Các từ vựng sử dụng:** `{', '.join(item['words'])}`")
                st.divider()
                st.markdown(item["content"])
