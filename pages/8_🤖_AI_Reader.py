import random
import requests
import datetime
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="AI Reading Assistant | Vocabulary Trainer", page_icon="🤖", layout="wide")

# --- CUSTOM CSS: NÂNG CẤP GIAO DIỆN CHUẨN MODERN SAAS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1050px;
    }
    
    /* Header & Subtitle */
    .app-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Document Paper Container cho bài đọc AI */
    .ai-paper {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 28px 32px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.04);
        margin-top: 15px;
        margin-bottom: 20px;
        line-height: 1.7;
        color: #334155;
    }

    /* Badges Cấp độ */
    .level-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-easy { background-color: #DCFCE7; color: #15803D; }
    .badge-normal { background-color: #E0F2FE; color: #0369A1; }
    .badge-hard { background-color: #FEE2E2; color: #B91C1C; }

    /* Quick Add Box */
    .quick-add-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div>
    <div class="app-title">AI Reading Assistant</div>
    <div class="app-subtitle">Tạo bài đọc hiểu và bài tập thực hành ngữ cảnh từ chính bộ sưu tập từ vựng cá nhân</div>
</div>
""", unsafe_allow_html=True)

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
if not isinstance(colloc_data, dict): colloc_data = {}
if not isinstance(vocab_data, dict): vocab_data = {}

user_all_words = list({**colloc_data, **vocab_data}.keys())

# Tạo 2 Tab
tab_create, tab_history = st.tabs(["🚀 Tạo bài đọc mới", "📜 Lịch sử tạo bài AI"])

# =========================================================
# TAB 1: TẠO BÀI ĐỌC MỚI
# =========================================================
with tab_create:
    if not user_all_words:
        st.info("💡 Kho từ vựng cá nhân của bạn hiện đang trống. Hãy sang mục **Add Word** hoặc **Library** để thêm từ trước nhé!")
    else:
        st.subheader("1. Chọn danh sách từ vựng")

        selected_words = st.multiselect(
            "Tích chọn các từ/cụm từ bạn muốn đưa vào bài tập:",
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
        st.subheader("2. Thiết lập cấu hình bài tập")
        
        col_type, col_level = st.columns([2, 1])
        
        with col_type:
            task_type = st.selectbox(
                "Dạng bài tập",
                [
                    "📝 Đoạn văn luyện dịch (Anh -> Việt) kèm chú thích từ",
                    "📖 Bài đọc hiểu Tiếng Anh + 3 câu hỏi trắc nghiệm",
                    "💬 Đoạn hội thoại thực tế giữa 2 người"
                ]
            )

        with col_level:
            difficulty = st.selectbox(
                "Cấp độ bài viết",
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

                with st.spinner("🤖 AI đang suy nghĩ và biên soạn bài tập cho bạn..."):
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
            st.write("")
            st.subheader("📄 Bài tập AI vừa tạo gần nhất")
            
            # Badge độ khó
            diff_str = latest_item.get('difficulty', 'Normal')
            if "Easy" in diff_str: badge_html = '<span class="level-badge badge-easy">EASY</span>'
            elif "Hard" in diff_str: badge_html = '<span class="level-badge badge-hard">HARD</span>'
            else: badge_html = '<span class="level-badge badge-normal">NORMAL</span>'

            st.caption(f"🕒 Tạo lúc: {latest_item['time']} | 🎯 Dạng: {latest_item['task_type']}")
            st.markdown(f"**Cấp độ:** {badge_html}", unsafe_allow_html=True)
            st.info(f"📌 Các từ vựng đưa vào bài: {', '.join([f'`{w}`' for w in latest_item['words']])}")
            
            # Render bài tập dạng Paper
            st.markdown(f"""
            <div class="ai-paper">
                {latest_item["content"]}
            </div>
            """, unsafe_allow_html=True)

            # --- KHU VỰC THÊM TỪ MỚI NHANH TỪ BÀI ĐỌC ---
            with st.expander("➕ Thấy từ mới trong bài đọc? Thêm nhanh vào kho từ vựng cá nhân!", expanded=False):
                col_w1, col_w2, col_w3 = st.columns([2, 2, 1])
                with col_w1:
                    new_w = st.text_input("Từ/Cụm từ mới:", key="add_quick_word", placeholder="e.g. permanent")
                with col_w2:
                    new_m = st.text_input("Nghĩa tiếng Việt:", key="add_quick_meaning", placeholder="e.g. vĩnh viễn")
                with col_w3:
                    target_repo = st.selectbox("Lưu vào kho:", ["Normal Vocab", "Collocations"], key="add_quick_repo")

                if st.button("📌 Lưu ngay vào Kho từ vựng", type="primary", use_container_width=True):
                    if not new_w or not new_m:
                        st.warning("⚠️ Vui lòng nhập đầy đủ Từ và Nghĩa!")
                    else:
                        clean_word = new_w.strip().lower()
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
            diff_tag = item.get('difficulty', 'Normal').split(" ")[0]
            with st.expander(f"📌 Bài #{len(ai_history) - idx} — {item['time']} [{diff_tag}] ({len(item['words'])} từ)"):
                st.caption(f"**Dạng bài:** {item['task_type']} | **Cấp độ:** {diff_tag}")
                st.write(f"**Từ vựng sử dụng:** {', '.join([f'`{w}`' for w in item['words']])}")
                st.markdown(f"""
                <div class="ai-paper">
                    {item["content"]}
                </div>
                """, unsafe_allow_html=True)
