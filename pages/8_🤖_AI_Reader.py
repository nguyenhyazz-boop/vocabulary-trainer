import random
import requests
import datetime
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="AI Assistant | Vocabulary Trainer", page_icon="🤖", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1050px;
    }
    
    .app-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    .svg-icon {
        display: inline-block;
        width: 18px;
        height: 18px;
        vertical-align: -3px;
        fill: currentColor;
    }

    .level-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-easy { background-color: #DCFCE7; color: #15803D; }
    .badge-normal { background-color: #E0F2FE; color: #0369A1; }
    .badge-hard { background-color: #FEE2E2; color: #B91C1C; }

    .word-chip {
        display: inline-block;
        background-color: #F1F5F9;
        color: #334155;
        border: 1px solid #E2E8F0;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)

ICON_ROBOT = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M12 2a2 2 0 0 1 2 2v1h1a3 3 0 0 1 3 3v2h2a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-2v3a3 3 0 0 1-3 3H9a3 3 0 0 1-3-3v-3H4a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1h2V8a3 3 0 0 1 3-3h1V4a2 2 0 0 1 2-2zm-3 8a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm6 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/></svg>'

st.markdown(f"""
<div>
    <div class="app-title">{ICON_ROBOT} AI Reading Assistant</div>
    <div class="app-subtitle">Tạo bài thực hành ngữ cảnh kèm từ điển mini từ bộ sưu tập từ vựng cá nhân</div>
</div>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username
history_file = f"ai_history_{username}.json"
clean_api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not clean_api_key:
    st.error("Hệ thống chưa được cấu hình API Key. Vui lòng thêm GEMINI_API_KEY vào Streamlit Secrets!")
    st.stop()

ai_history = load_data(history_file)
if not isinstance(ai_history, list): ai_history = []

colloc_data = load_data(f"data_collocation_{username}.json")
vocab_data = load_data(f"data_vocab_{username}.json")
if not isinstance(colloc_data, dict): colloc_data = {}
if not isinstance(vocab_data, dict): vocab_data = {}

user_all_words = list({**colloc_data, **vocab_data}.keys())

tab_create, tab_history = st.tabs(["Tạo bài đọc mới", "Lịch sử tạo bài AI"])

with tab_create:
    if not user_all_words:
        st.info("Kho từ vựng cá nhân của bạn hiện đang trống. Hãy sang mục Add Word hoặc Library để thêm từ trước nhé!")
    else:
        st.subheader("1. Chọn từ vựng luyện tập")

        if "reader_selected_words" not in st.session_state:
            st.session_state.reader_selected_words = user_all_words[:min(5, len(user_all_words))]

        col_quick1, col_quick2 = st.columns(2)
        with col_quick1:
            if st.button("🎲 AI chọn ngẫu nhiên 5 từ", use_container_width=True):
                st.session_state.reader_selected_words = random.sample(user_all_words, min(5, len(user_all_words)))
                st.rerun()

        with col_quick2:
            if st.button("🎲 AI chọn ngẫu nhiên 8 từ", use_container_width=True):
                st.session_state.reader_selected_words = random.sample(user_all_words, min(8, len(user_all_words)))
                st.rerun()

        selected_words = st.multiselect(
            "Tích chọn các từ muốn luyện tập:",
            options=user_all_words,
            key="reader_selected_words"
        )

        st.write("")
        st.subheader("2. Thiết lập cấu hình bài tập")
        
        col_type, col_level = st.columns([2, 1])
        
        with col_type:
            task_type = st.selectbox(
                "Dạng bài tập",
                [
                    "Đoạn văn ngắn (3-4 câu)",
                    "Hội thoại ngắn"
                ]
            )

        with col_level:
            difficulty = st.selectbox(
                "Cấp độ bài viết",
                [
                    "Easy (Đơn giản, dễ hiểu)",
                    "Normal (Vừa sức, tự nhiên)",
                    "Hard (Nâng cao, học thuật)"
                ]
            )

        st.divider()

        if st.button("Tạo Bài Tập Ngay", type="primary", use_container_width=True):
            if not selected_words:
                st.warning("Bạn chưa chọn từ vựng nào!")
            else:
                words_str = ", ".join([f"'{w}'" for w in selected_words])

                # Dùng System Instruction để "tẩy não" AI
                system_instruction = """You are an automated exercise generator. You NEVER use conversational text, greetings, reasoning, or thinking traces. You output ONLY the exact requested markdown format: 
1. The paragraph.
2. A divider (---).
3. The bulleted dictionary. 
Nothing before, nothing after."""

                prompt_text = f"""Create an English reading practice using these words: [{words_str}]. Level: {difficulty}.

FORMAT:
[Paragraph: 3 to 4 sentences. Bold target words like **this**]

---
### 📚 Mini Dictionary
* **word**: short Vietnamese meaning
"""

                payload = {
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    },
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "generationConfig": {
                        "temperature": 0.2
                    }
                }

                with st.spinner("AI đang tạo bài tập..."):
                    headers = {"Content-Type": "application/json"}

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
                        working_models = ["gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro"]

                    success = False
                    last_error = ""

                    for model_name in working_models:
                        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={clean_api_key}"
                        try:
                            res = requests.post(url, json=payload, headers=headers, timeout=30)
                            res_data = res.json()

                            if res.status_code == 200:
                                raw_text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                                
                                new_entry = {
                                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "task_type": task_type,
                                    "difficulty": difficulty,
                                    "words": selected_words,
                                    "content": raw_text
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
                        st.error(f"Có lỗi kết nối AI: {last_error}")

        if ai_history:
            latest_item = ai_history[0]
            st.write("")
            st.subheader("Bài tập AI vừa tạo gần nhất")
            
            diff_str = latest_item.get('difficulty', 'Normal')
            if "Easy" in diff_str: badge_html = '<span class="level-badge badge-easy">EASY</span>'
            elif "Hard" in diff_str: badge_html = '<span class="level-badge badge-hard">HARD</span>'
            else: badge_html = '<span class="level-badge badge-normal">NORMAL</span>'

            st.caption(f"Tạo lúc: {latest_item['time']} | Dạng: {latest_item['task_type']}")
            st.markdown(f"**Cấp độ:** {badge_html}", unsafe_allow_html=True)
            
            chips_html = "".join([f'<span class="word-chip">{w}</span>' for w in latest_item['words']])
            st.markdown(f"<div style='margin-top: 8px; margin-bottom: 12px;'><b>Từ vựng đưa vào bài:</b><br>{chips_html}</div>", unsafe_allow_html=True)
            
            with st.container(border=True):
                st.markdown(latest_item["content"])

            with st.expander("Thấy từ mới trong bài đọc? Thêm nhanh vào kho từ vựng cá nhân!", expanded=False):
                col_w1, col_w2, col_w3 = st.columns([2, 2, 1])
                with col_w1:
                    new_w = st.text_input("Từ/Cụm từ mới:", key="add_quick_word", placeholder="e.g. permanent")
                with col_w2:
                    new_m = st.text_input("Nghĩa tiếng Việt:", key="add_quick_meaning", placeholder="e.g. vĩnh viễn")
                with col_w3:
                    target_repo = st.selectbox("Lưu vào kho:", ["Normal Vocab", "Collocations"], key="add_quick_repo")

                if st.button("Lưu vào Kho từ vựng", type="primary", use_container_width=True):
                    if not new_w or not new_m:
                        st.warning("Vui lòng nhập đầy đủ Từ và Nghĩa!")
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
                        st.success(f"Đã thêm từ '{clean_word}' vào kho {target_repo} thành công!")
                        st.rerun()

with tab_history:
    st.subheader("Danh sách bài đọc AI đã lưu")
    
    if not ai_history:
        st.info("Chưa có lịch sử bài đọc nào được lưu. Hãy tạo bài đọc mới ở Tab 'Tạo bài đọc mới' nhé!")
    else:
        if st.button("Xóa toàn bộ lịch sử bài đọc", type="secondary"):
            save_data([], history_file)
            st.success("Đã xóa sạch lịch sử!")
            st.rerun()

        st.write("---")

        for idx, item in enumerate(ai_history):
            diff_tag = item.get('difficulty', 'Normal').split(" ")[0]
            with st.expander(f"Bài #{len(ai_history) - idx} — {item['time']} [{diff_tag}] ({len(item['words'])} từ)"):
                st.caption(f"**Dạng bài:** {item['task_type']} | **Cấp độ:** {diff_tag}")
                st.write(f"**Từ vựng sử dụng:** {', '.join([f'`{w}`' for w in item['words']])}")
                with st.container(border=True):
                    st.markdown(item["content"])
