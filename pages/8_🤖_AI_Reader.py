import random
import requests
import datetime
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="AI Reading Assistant - Vocabulary Trainer", page_icon="🤖", layout="wide")

st.title("🤖 AI Reading Assistant")
st.caption("Tạo bài đọc hiểu / luyện tập từ vựng cá nhân phân theo cấp độ phù hợp!")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username
history_file = f"ai_history_{username}.json"

# Lấy API Key tự động từ Streamlit Secrets
clean_api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not clean_api_key:
    st.error("⚠️ Hệ thống chưa được cấu hình API Key. Vui lòng thêm GEMINI_API_KEY vào Streamlit Secrets!")
    st.stop()

# Đọc lịch sử bài học AI đã lưu của User
ai_history = load_data(history_file)
if not isinstance(ai_history, list):
    ai_history = []

# Đọc kho từ vựng cá nhân
colloc_data = load_data(f"data_collocation_{username}.json")
vocab_data = load_data(f"data_vocab_{username}.json")
user_all_words = list({**colloc_data, **vocab_data}.keys())

# Tạo 2 Tab
tab_create, tab_history = st.tabs(["🚀 Tạo bài đọc mới", "📜 Lịch sử tạo bài AI"])

# =========================================================
# TAB 1: TẠO BÀI ĐỌC MỚI
# =========================================================
with tab_create:
    if not user_all_words:
        st.warning("⚠️ Kho từ vựng cá nhân của bạn hiện đang trống. Hãy sang mục **Library** để thêm từ trước nhé!")
    else:
        st.subheader("🎯 Thiết lập bài tập AI")

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
        
        # CHỌN DẠNG BÀI VÀ CẤP ĐỘ
        col_type, col_level = st.columns([2, 1])
        
        with col_type:
            task_type = st.selectbox(
                "Chọn dạng bài tập bạn muốn luyện:",
                [
                    "📝 Đoạn văn luyện dịch (Anh -> Việt) kèm chú thích từ",
                    "📖 Bài đọc hiểu Tiếng Anh + 3 câu hỏi trắc nghiệm",
                    "💬 Đoạn hội thoại thực tế giữa 2 người"
                ]
            )

        with col_level:
            difficulty = st.selectbox(
                "Chọn cấp độ bài viết:",
                [
                    "🌱 Easy (Đơn giản, câu ngắn)",
                    "⚡ Normal (Trung bình, vừa sức)",
                    "🔥 Hard (Nâng cao, học thuật)"
                ]
            )

        st.divider()

        if st.button("🚀 AI Tạo Bài Tập Ngay", type="primary", use_container_width=True):
            if not selected_words:
                st.warning("⚠️ Bạn chưa chọn từ vựng nào cả!")
            else:
                words_str = ", ".join([f"'{w}'" for w in selected_words])

                # Hướng dẫn độ khó tương ứng cho AI
                level_instructions = {
                    "🌱 Easy (Đơn giản, câu ngắn)": "Dùng từ vựng đơn giản, câu ngắn gọn, cấu trúc ngữ pháp cơ bản dễ hiểu, phù hợp người mới học.",
                    "⚡ Normal (Trung bình, vừa sức)": "Dùng ngữ pháp và từ vựng thông dụng hàng ngày, độ dài vừa phải, văn phong tự nhiên.",
                    "🔥 Hard (Nâng cao, học thuật)": "Dùng cấu trúc câu phức hợp, văn phong học thuật/chuyên nghiệp, câu dài chứa nhiều thông tin chi tiết."
                }

                prompt_text = f"""
Hãy đóng vai một giáo viên Tiếng Anh xuất sắc. 

Nhiệm vụ: Viết một bài tập Tiếng Anh dựa trên danh sách từ/cụm từ sau: [{words_str}].

CẤP ĐỘ BÀI VIẾT: {difficulty}
Yêu cầu độ khó: {level_instructions[difficulty]}

YÊU CẦU BẮT BUỘC:
1. Dạng bài yêu cầu: {task_type}.
2. Trong phần văn bản tiếng Anh, hãy **in đậm** (bold) chính xác các từ/cụm từ trong danh sách trên mỗi khi chúng xuất hiện.
3. Nội dung bài viết phải mạch lạc, chuẩn ngữ pháp và tuân thủ đúng CẤP ĐỘ đã chọn.
4. Ở cuối bài, cung cấp một danh sách tổng hợp lại các từ vựng đã dùng kèm giải nghĩa tiếng Việt ngắn gọn.
5. KHÔNG lặp lại các câu hướng dẫn, KHÔNG in ra prompt. Bắt đầu ngay vào tiêu đề và nội dung bài tập.
"""

                with st.spinner(f"🤖 AI đang tạo bài đọc cấp độ {difficulty} cho bạn..."):
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
                                    "difficulty": difficulty,
                                    "words": selected_words,
                                    "content": result_text
                                }
                                
                                ai_history.insert(0, new_entry)
                                save_data(ai_history, history_file)
                                
                                success = True
                                st.balloons()
                                st.success(f"🎉 Đã tạo bài tập ({difficulty}) thành công!")
                                st.rerun()
                                break
                            else:
                                last_error = res_data.get("error", {}).get("message", res.text)
                        except Exception as e:
                            last_error = str(e)
                            continue

                    if not success:
                        st.error(f"❌ Có lỗi kết nối AI: {last_error}")

        # Hiển thị bài đọc vừa tạo gần nhất
        if ai_history:
            latest_item = ai_history[0]
            st.write("---")
            st.subheader("📄 Bài tập vừa tạo gần nhất:")
            st.caption(f"🕒 {latest_item['time']} | 🎯 {latest_item['task_type']} | 💪 Cấp độ: **{latest_item.get('difficulty', 'Sơ cấp')}**")
            st.info(f"📌 Từ vựng: {', '.join(latest_item['words'])}")
            st.markdown(latest_item["content"])

            # --- KHU VỰC THÊM TỪ MỚI NHANH TỪ BÀI ĐỌC ---
            st.divider()
            with st.expander("➕ Thấy từ mới trong bài đọc? Thêm nhanh vào kho từ vựng ngay tại đây!", expanded=True):
                col_w1, col_w2, col_w3 = st.columns([2, 2, 1])
                with col_w1:
                    new_w = st.text_input("Từ/Cụm từ mới:", key="add_quick_word", placeholder="vd: permanent")
                with col_w2:
                    new_m = st.text_input("Nghĩa của từ:", key="add_quick_meaning", placeholder="vd: lặp lại, vĩnh viễn")
                with col_w3:
                    target_repo = st.selectbox("Lưu vào kho:", ["Normal Vocab", "Collocations"], key="add_quick_repo")

                if st.button("📌 Lưu ngay vào Kho từ vựng", type="primary", use_container_width=True):
                    if not new_w or not new_m:
                        st.warning("⚠️ Vui lòng nhập đầy đủ Từ và Nghĩa!")
                    else:
                        clean_word = new_w.strip()
                        clean_meaning = new_m.strip()
                        
                        if target_repo == "Collocations":
                            target_file = f"data_collocation_{username}.json"
                            repo_data = colloc_data
                        else:
                            target_file = f"data_vocab_{username}.json"
                            repo_data = vocab_data

                        repo_data[clean_word] = {
                            "meaning": clean_meaning,
                            "correct": 0,
                            "wrong": 0
                        }
                        save_data(repo_data, target_file)
                        st.success(f"🎉 Đã thêm từ **'{clean_word}'** vào kho **{target_repo}** thành công!")
                        st.rerun()


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
            diff_tag = item.get('difficulty', 'Vừa sức')
            with st.expander(f"📌 Bài #{len(ai_history) - idx} - {item['time']} [{diff_tag}] ({len(item['words'])} từ)"):
                st.caption(f"**Dạng bài:** {item['task_type']} | **Cấp độ:** {diff_tag}")
                st.write(f"**Các từ vựng sử dụng:** `{', '.join(item['words'])}`")
                st.divider()
                st.markdown(item["content"])
