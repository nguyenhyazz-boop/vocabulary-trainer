import random
import re
import urllib.parse
import requests
import datetime
import json
import streamlit as st
from utils.data_manager import load_data, save_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="AI Reader | Vocabulary Trainer", page_icon="📖", layout="wide")
apply_global_theme("8_AI_Reader")

# --- HÀM TỰ ĐỘNG BÔI ĐẬM TỪ VỰNG TRONG CÂU VÍ DỤ ---
def highlight_word_in_example(word: str, example: str) -> str:
    if not word or not example:
        return example
    clean_w = word.strip()
    if not clean_w:
        return example
    if f"**{clean_w.lower()}**" in example.lower():
        return example
    pattern = re.compile(re.escape(clean_w), re.IGNORECASE)
    return pattern.sub(lambda m: f"**{m.group(0)}**", example)

# --- HÀM AI TỰ PHÂN TÍCH LOẠI TỪ, NGHĨA & CÂU VÍ DỤ ---
def quick_analyze_word(word: str, api_key: str):
    prompt = (
        f"Bạn là trợ lý học từ vựng tiếng Anh cho học sinh Việt Nam ôn thi THPT. "
        f"Hãy phân tích từ/cụm từ tiếng Anh: '{word}'. "
        f"Trả về DUY NHẤT một chuỗi JSON hợp lệ (không giải thích thêm) theo định dạng:\n"
        f'{{"pos": "loại từ tiếng Anh ngắn gọn (chỉ chọn 1 trong: Noun, Verb, Adjective, Adverb, Phrase, Preposition, Other)", '
        f'"meaning": "nghĩa tiếng Việt ngắn gọn, sát nghĩa nhất (tối đa 6-8 từ)", '
        f'"example": "1 câu ví dụ tiếng Anh cơ bản, tự nhiên có chứa chính xác từ/cụm từ đó"}}'
    )

    if api_key:
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            list_res = requests.get(list_url, timeout=10)
            exclude_kw = ("exp", "thinking", "audio", "image", "tts", "vision", "embedding", "aqa")
            candidates = []
            if list_res.status_code == 200:
                for m in list_res.json().get("models", []):
                    m_name = m.get("name", "")
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        if "gemini" in m_name.lower() and not any(k in m_name.lower() for k in exclude_kw):
                            candidates.append(m_name)
            candidates.sort(key=lambda x: (0 if "flash" in x else 1, x))

            for model_path in candidates[:4]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={api_key}"
                    payload = {
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.3}
                    }
                    res = requests.post(url, json=payload, timeout=15)
                    if res.status_code == 200:
                        raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                        if json_match:
                            parsed = json.loads(json_match.group(0))
                            return (
                                parsed.get("pos", "Other"),
                                parsed.get("meaning", ""),
                                parsed.get("example", ""),
                                None
                            )
                except Exception:
                    continue
        except Exception:
            pass

    try:
        from deep_translator import GoogleTranslator
        vi_meaning = GoogleTranslator(source="en", target="vi").translate(word)
        ex_sentence = ""
        detected_pos = "Phrase" if " " in word.strip() else "Other"
        try:
            dict_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word.lower())}"
            dr = requests.get(dict_url, timeout=8)
            if dr.status_code == 200:
                for entry in dr.json():
                    for m in entry.get("meanings", []):
                        if m.get("partOfSpeech") and detected_pos == "Other":
                            detected_pos = m["partOfSpeech"].capitalize()
                        for d in m.get("definitions", []):
                            if d.get("example"):
                                ex_sentence = d["example"]
                                break
                        if ex_sentence:
                            break
                    if ex_sentence:
                        break
        except Exception:
            pass
        if not ex_sentence:
            ex_sentence = f"We need to learn how to use '{word}' correctly in a sentence."
        return detected_pos, vi_meaning, ex_sentence, None
    except Exception as e:
        return None, None, None, f"Không thể phân tích từ vựng lúc này: {e}"

# --- CUSTOM CSS: WARM EDITORIAL AI READER ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 980px !important;
    }

    .reader-sub {
        font-size: 0.82rem;
        font-weight: 700;
        color: #78716C;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .reader-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }
    .reader-desc {
        color: #57534E;
        font-size: 0.94rem;
        margin-top: 4px;
        margin-bottom: 1.4rem;
    }

    /* Thẻ bọc từng bước cấu hình */
    .step-card {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 20px;
        padding: 20px 24px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(28, 25, 23, 0.02);
    }
    .step-kicker {
        font-size: 0.72rem;
        font-weight: 800;
        color: #7C3AED;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 3px;
    }
    .step-heading {
        font-size: 1.15rem;
        font-weight: 800;
        color: #1C1917;
        margin-bottom: 12px;
    }

    /* Tag từ vựng đã chọn dịu mắt theo tông Editorial */
    span[data-baseweb="tag"] {
        background-color: #EFECE3 !important;
        color: #1C1917 !important;
        border: 1px solid #DFD9C8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] span {
        color: #1C1917 !important;
    }
    span[data-baseweb="tag"] svg {
        fill: #57534E !important;
    }

    /* Badge cấp độ */
    .level-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.5px;
    }
    .badge-easy { background-color: #DCFCE7; color: #15803D; }
    .badge-normal { background-color: #EDE9FE; color: #7C3AED; }
    .badge-hard { background-color: #FEF3C7; color: #B45309; }

    /* Chip từ vựng trong bài đọc */
    .word-chip {
        display: inline-block;
        background-color: #FAF8F2;
        color: #1C1917;
        border: 1px solid #E7E2D6;
        padding: 4px 11px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Khung bài đọc kiểu tạp chí */
    .passage-shell {
        background-color: #EFECE3;
        border: 1px solid #E5DFD2;
        border-radius: 22px;
        padding: 14px;
        margin-top: 8px;
        margin-bottom: 14px;
    }
    .passage-paper {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 16px;
        padding: 24px 26px;
        color: #1C1917;
        line-height: 1.75;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div>
    <div class="reader-sub">Contextual Reading Studio</div>
    <div class="reader-title">AI Reading Assistant</div>
    <div class="reader-desc">Tạo bài thực hành ngữ cảnh kèm từ điển mini từ bộ sưu tập từ vựng cá nhân</div>
</div>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username
history_file = f"ai_history_{username}.json"
clean_api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

if not clean_api_key:
    st.error("Hệ thống chưa được cấu hình API Key. Vui lòng thêm GEMINI_API_KEY vào Streamlit Secrets!")
    st.stop()

ai_history = load_data(history_file)
if not isinstance(ai_history, list):
    ai_history = []

colloc_data = load_data(f"data_collocation_{username}.json")
vocab_data = load_data(f"data_vocab_{username}.json")
if not isinstance(colloc_data, dict):
    colloc_data = {}
if not isinstance(vocab_data, dict):
    vocab_data = {}

user_all_words = list({**colloc_data, **vocab_data}.keys())

tab_create, tab_history = st.tabs(["Create Reading", "Saved History"])

with tab_create:
    if not user_all_words:
        st.info("Kho từ vựng cá nhân của bạn hiện đang trống. Hãy sang mục Add Word hoặc Library để thêm từ trước nhé!")
    else:
        # --- BƯỚC 1: CHỌN TỪ VỰNG ---
        st.markdown("""
        <div class="step-card">
            <div class="step-kicker">Step 01 · Word Selection</div>
            <div class="step-heading">Chọn từ vựng luyện tập</div>
        """, unsafe_allow_html=True)

        if "reader_selected_words" not in st.session_state:
            st.session_state.reader_selected_words = user_all_words[:min(5, len(user_all_words))]

        col_quick1, col_quick2 = st.columns(2, gap="medium")
        with col_quick1:
            if st.button("Random 5 Words", use_container_width=True):
                st.session_state.reader_selected_words = random.sample(user_all_words, min(5, len(user_all_words)))
                st.rerun()

        with col_quick2:
            if st.button("Random 8 Words", use_container_width=True):
                st.session_state.reader_selected_words = random.sample(user_all_words, min(8, len(user_all_words)))
                st.rerun()

        st.write("")
        selected_words = st.multiselect(
            "Tích chọn các từ muốn đưa vào bài đọc:",
            options=user_all_words,
            key="reader_selected_words"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # --- BƯỚC 2: CẤU HÌNH BÀI TẬP ---
        st.markdown("""
        <div class="step-card">
            <div class="step-kicker">Step 02 · Configuration</div>
            <div class="step-heading">Thiết lập cấu hình bài tập</div>
        """, unsafe_allow_html=True)

        col_type, col_level = st.columns([1.8, 1], gap="medium")

        with col_type:
            task_type = st.selectbox(
                "Dạng bài tập",
                [
                    "Đoạn văn thực tế (Độ dài tùy theo số từ)",
                    "Đoạn hội thoại thực tế"
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

        st.write("")
        if st.button("Generate Reading Passage  ↗", type="primary", use_container_width=True):
            if not selected_words:
                st.warning("Bạn chưa chọn từ vựng nào!")
            else:
                words_str = ", ".join([f"'{w}'" for w in selected_words])

                prompt_text = f"Write a detailed {task_type} naturally integrating all of these words: [{words_str}]. Level: {difficulty}. Ensure the text is long enough to provide a clear and natural context for every single target word (at least 5-8 sentences or longer if needed). Bold all the target words."

                payload = {
                    "contents": [{"parts": [{"text": prompt_text}]}],
                    "generationConfig": {
                        "temperature": 0.4,
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "OBJECT",
                            "properties": {
                                "paragraph": {
                                    "type": "STRING",
                                    "description": "The English paragraph or conversation. Write naturally and beautifully. The length must be proportional to the number of provided words (long enough to make sense). Target words must be bolded."
                                },
                                "vocabulary": {
                                    "type": "ARRAY",
                                    "description": "List of the target words used in the text.",
                                    "items": {
                                        "type": "OBJECT",
                                        "properties": {
                                            "word": {"type": "STRING"},
                                            "meaning": {"type": "STRING", "description": "Short Vietnamese meaning of the word."}
                                        },
                                        "required": ["word", "meaning"]
                                    }
                                }
                            },
                            "required": ["paragraph", "vocabulary"]
                        }
                    }
                }

                with st.spinner("AI đang sáng tác bài học thực tế cho bạn..."):
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

                                try:
                                    ai_data = json.loads(raw_text)
                                    paragraph = ai_data.get("paragraph", "")
                                    vocab_list = ai_data.get("vocabulary", [])

                                    clean_content = paragraph + "\n\n---\n### Mini Dictionary\n"
                                    for v in vocab_list:
                                        clean_content += f"- **{v.get('word', '')}**: {v.get('meaning', '')}\n"

                                except json.JSONDecodeError:
                                    clean_content = "Đã xảy ra lỗi khi xử lý dữ liệu từ AI. Vui lòng thử lại!"

                                new_entry = {
                                    "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "task_type": task_type,
                                    "difficulty": difficulty,
                                    "words": selected_words,
                                    "content": clean_content
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

        st.markdown("</div>", unsafe_allow_html=True)

        # --- KẾT QUẢ BÀI ĐỌC VỪA TẠO ---
        if ai_history:
            latest_item = ai_history[0]
            st.write("")
            st.markdown('<div class="reader-sub">Latest Generated Passage</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:1.35rem; font-weight:800; color:#1C1917; margin-bottom:6px;">Bài tập AI vừa tạo gần nhất</div>', unsafe_allow_html=True)

            diff_str = latest_item.get("difficulty", "Normal")
            if "Easy" in diff_str:
                badge_html = '<span class="level-badge badge-easy">EASY</span>'
            elif "Hard" in diff_str:
                badge_html = '<span class="level-badge badge-hard">HARD</span>'
            else:
                badge_html = '<span class="level-badge badge-normal">NORMAL</span>'

            st.caption(f"Tạo lúc: {latest_item['time']} · Dạng: {latest_item['task_type']}")
            st.markdown(f"<div style='margin:6px 0 10px 0;'>{badge_html}</div>", unsafe_allow_html=True)

            chips_html = "".join([f'<span class="word-chip">{w}</span>' for w in latest_item["words"]])
            st.markdown(f"<div style='margin-bottom:10px;'>{chips_html}</div>", unsafe_allow_html=True)

            st.markdown('<div class="passage-shell"><div class="passage-paper">', unsafe_allow_html=True)
            st.markdown(latest_item["content"])
            st.markdown('</div></div>', unsafe_allow_html=True)

            with st.expander("Thấy từ mới trong bài đọc? Thêm nhanh vào kho từ vựng cá nhân", expanded=False):
                col_w1, col_w2 = st.columns([3, 1.5], gap="medium")
                with col_w1:
                    new_w = st.text_input("Từ / Cụm từ mới:", key="add_quick_word", placeholder="e.g. permanent, take action")
                with col_w2:
                    target_repo = st.selectbox("Lưu vào kho:", ["Normal Vocab", "Collocations"], key="add_quick_repo")

                if st.button("AI Phân tích & Lưu vào Kho", type="primary", use_container_width=True):
                    if not new_w.strip():
                        st.warning("Vui lòng nhập Từ / Cụm từ mới!")
                    else:
                        with st.spinner("AI đang tự xác định loại từ, dịch nghĩa & tạo câu ví dụ..."):
                            ai_pos, ai_meaning, ai_example, err = quick_analyze_word(new_w.strip(), clean_api_key)
                            if err or not ai_meaning:
                                st.error(err or "Không thể phân tích từ vựng lúc này!")
                            else:
                                clean_word = new_w.strip().lower()
                                clean_pos = ai_pos.strip() if ai_pos else "Other"
                                final_example = highlight_word_in_example(new_w.strip(), ai_example)

                                if target_repo == "Collocations":
                                    target_file = f"data_collocation_{username}.json"
                                    repo_data = colloc_data
                                else:
                                    target_file = f"data_vocab_{username}.json"
                                    repo_data = vocab_data

                                repo_data[clean_word] = {
                                    "meaning": ai_meaning.strip(),
                                    "pos": clean_pos,
                                    "example": final_example,
                                    "correct": repo_data.get(clean_word, {}).get("correct", 0),
                                    "wrong": repo_data.get(clean_word, {}).get("wrong", 0)
                                }
                                save_data(repo_data, target_file)
                                st.success(f"Đã lưu '{clean_word}' [{clean_pos}] — {ai_meaning.strip()} vào kho {target_repo}!")

with tab_history:
    st.markdown('<div style="font-size:1.25rem; font-weight:800; color:#1C1917; margin-bottom:10px;">Danh sách bài đọc AI đã lưu</div>', unsafe_allow_html=True)

    if not ai_history:
        st.info("Chưa có lịch sử bài đọc nào được lưu. Hãy tạo bài đọc mới ở Tab 'Create Reading' nhé!")
    else:
        if st.button("Clear All History", type="secondary"):
            save_data([], history_file)
            st.toast("Đã xóa sạch lịch sử!")
            st.rerun()

        st.write("")

        for idx, item in enumerate(ai_history):
            diff_tag = item.get("difficulty", "Normal").split(" ")[0]
            with st.expander(f"Passage #{len(ai_history) - idx} — {item['time']} [{diff_tag}] ({len(item['words'])} words)"):
                st.caption(f"Dạng bài: {item['task_type']} · Cấp độ: {diff_tag}")
                chips = "".join([f'<span class="word-chip">{w}</span>' for w in item["words"]])
                st.markdown(f"<div style='margin-bottom:10px;'>{chips}</div>", unsafe_allow_html=True)
                st.markdown('<div class="passage-shell"><div class="passage-paper">', unsafe_allow_html=True)
                st.markdown(item["content"])
                st.markdown('</div></div>', unsafe_allow_html=True)
