import json
import re
import urllib.request
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Add Word | Vocabulary Trainer", page_icon="📝", layout="wide")

# --- HÀM GỌI AI TỰ ĐỘNG PHÂN TÍCH NGHĨA & VÍ DỤ ---
def auto_analyze_word(word: str, pos: str):
    groq_key = st.secrets.get("GROQ_API_KEY", "")
    gemini_key = st.secrets.get("GEMINI_API_KEY", "")

    prompt = (
        f"Bạn là trợ lý học từ vựng tiếng Anh cho học sinh Việt Nam ôn thi THPT. "
        f"Hãy phân tích từ/cụm từ tiếng Anh: '{word}' với loại từ '{pos}'. "
        f"Trả về DUY NHẤT một chuỗi JSON hợp lệ (không markdown, không giải thích thêm) theo định dạng:\n"
        f'{{"meaning": "nghĩa tiếng Việt ngắn gọn, sát nghĩa nhất (tối đa 6-8 từ)", '
        f'"example": "1 câu ví dụ tiếng Anh cơ bản, tự nhiên có chứa chính xác từ/cụm từ đó"}}'
    )

    # Ưu tiên 1: Groq API (siêu nhanh)
    if groq_key:
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {groq_key}",
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return parsed.get("meaning", ""), parsed.get("example", ""), None
        except Exception as e:
            return None, None, f"Lỗi Groq API: {e}"

   # Ưu tiên 2: Gemini API (Tự động tìm model khả dụng của API Key)
    if gemini_key:
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
            with urllib.request.urlopen(list_url, timeout=10) as r:
                models_data = json.loads(r.read().decode("utf-8"))

            valid_models = [
                m["name"] for m in models_data.get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
                and "flash" in m["name"].lower()
            ]
            if not valid_models:
                valid_models = [
                    m["name"] for m in models_data.get("models", [])
                    if "generateContent" in m.get("supportedGenerationMethods", [])
                ]

            model_path = valid_models[0]  # Ví dụ: "models/gemini-2.0-flash"
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json"}
            }
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(content)
                return parsed.get("meaning", ""), parsed.get("example", ""), None
        except Exception as e:
            return None, None, f"Lỗi Gemini API: {e}"
# --- CUSTOM CSS: MODERN SAAS STYLING ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1000px;
    }
    
    .app-header {
        margin-bottom: 2rem;
    }
    .app-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.9rem;
    }

    /* Thẻ Container xem trước (Live Preview Card) */
    .preview-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease-in-out;
    }
    .preview-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
    }
    .preview-word {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0F172A;
    }
    
    /* Badge loại từ phong cách Minimalist */
    .pos-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .badge-noun { background-color: #E0F2FE; color: #0369A1; }
    .badge-verb { background-color: #DCFCE7; color: #15803D; }
    .badge-adj { background-color: #FEF9C3; color: #A16207; }
    .badge-adv { background-color: #F3E8FF; color: #7E22CE; }
    .badge-phrase { background-color: #FFEDD5; color: #C2410C; }
    .badge-other { background-color: #F1F5F9; color: #475569; }

    .preview-meaning {
        font-size: 1rem;
        color: #334155;
        margin-top: 8px;
        font-weight: 500;
    }
    .preview-example {
        font-size: 0.85rem;
        color: #64748B;
        font-style: italic;
        margin-top: 8px;
        padding-left: 8px;
        border-left: 2px solid #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# --- GIỚI THIỆU HEADER ---
st.markdown("""
<div class="app-header">
    <div class="app-title">Add New Word</div>
    <div class="app-subtitle">Thêm và phân loại từ vựng mới vào bộ sưu tập cá nhân (Hỗ trợ AI tự động dịch nghĩa & tạo ví dụ)</div>
</div>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Khởi tạo session_state cho các ô nhập liệu để AI có thể tự động điền giá trị
if "add_meaning_val" not in st.session_state:
    st.session_state.add_meaning_val = ""
if "add_example_val" not in st.session_state:
    st.session_state.add_example_val = ""

# --- CHỌN KHO LƯU TRỮ ---
category = st.radio(
    "Kho lưu trữ",
    ["Vocabulary (Từ đơn)", "Collocation (Cụm từ)"],
    horizontal=True,
    label_visibility="collapsed"
)

if "Collocation" in category:
    file_name = f"data_collocation_{username}.json"
else:
    file_name = f"data_vocab_{username}.json"

current_data = load_data(file_name)
if not isinstance(current_data, dict):
    current_data = {}

st.write("")

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

# --- CHIA 2 CỘT: CỘT NHẬP FORM & CỘT LIVE PREVIEW ---
col_form, col_preview = st.columns([3, 2], gap="large")

with col_form:
    st.subheader("Thông tin từ vựng")
    
    new_word = st.text_input("Từ / Cụm từ Tiếng Anh", placeholder="e.g. account, take action").strip()
    
    col_pos, col_ai = st.columns([1.3, 1])
    with col_pos:
        word_pos = st.selectbox(
            "Loại từ (Part of Speech)",
            [
                "Noun (n)",
                "Verb (v)",
                "Adjective (adj)",
                "Adverb (adv)",
                "Phrase / Idiom",
                "Preposition (prep)",
                "Other"
            ]
        )
    with col_ai:
        st.write("")
        st.write("")
        if st.button("✨ AI Dịch & Tạo ví dụ", use_container_width=True):
            if not new_word:
                st.warning("Hãy nhập từ tiếng Anh trước nhé!")
            else:
                with st.spinner("AI đang phân tích từ vựng..."):
                    ai_vi, ai_ex, err = auto_analyze_word(new_word, word_pos)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.add_meaning_val = ai_vi
                        st.session_state.add_example_val = ai_ex
                        st.rerun()

    new_meaning = st.text_input(
        "Nghĩa Tiếng Việt",
        key="add_meaning_val",
        placeholder="e.g. câu chuyện, bản báo cáo"
    ).strip()

    example_sentence = st.text_area(
        "Câu ví dụ (Tự động in đậm từ vựng)",
        key="add_example_val",
        placeholder="e.g. She gave a detailed account of the event.",
        height=80
    ).strip()

    st.write("")
    submitted = st.button("Lưu Từ Vựng", type="primary", use_container_width=True)

# --- CỘT LIVE PREVIEW (XEM TRƯỚC THẺ TỪ) ---
with col_preview:
    st.subheader("Xem trước thẻ từ")
    
    pos_short = word_pos.split(" ")[0].lower()
    badge_class = f"badge-{pos_short}" if pos_short in ["noun", "verb", "adj", "adv", "phrase"] else "badge-other"
    
    display_word = new_word if new_word else "Word Preview"
    display_meaning = new_meaning if new_meaning else "Nghĩa của từ sẽ hiển thị ở đây..."
    
    if example_sentence and new_word:
        auto_highlighted_preview = highlight_word_in_example(new_word, example_sentence)
        preview_html_example = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', auto_highlighted_preview)
        display_example = f'"{preview_html_example}"'
    elif example_sentence:
        display_example = f'"{example_sentence}"'
    else:
        display_example = '"Câu ví dụ minh họa sẽ hiển thị ở đây..."'

    st.markdown(f"""
    <div class="preview-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span class="preview-word">{display_word}</span>
            <span class="pos-badge {badge_class}">{word_pos.split(' ')[0]}</span>
        </div>
        <div class="preview-meaning">{display_meaning}</div>
        <div class="preview-example">{display_example}</div>
    </div>
    """, unsafe_allow_html=True)

# --- XỬ LÝ LƯU DỮ LIỆU ---
if submitted:
    if not new_word or not new_meaning:
        st.error("Vui lòng nhập đầy đủ Từ tiếng Anh và Nghĩa tiếng Việt!")
    else:
        word_key = new_word.lower()
        pos_code = word_pos.split(" ")[0]

        final_example = highlight_word_in_example(new_word, example_sentence)

        current_data[word_key] = {
            "meaning": new_meaning,
            "pos": pos_code,
            "example": final_example,
            "correct": current_data.get(word_key, {}).get("correct", 0),
            "wrong": current_data.get(word_key, {}).get("wrong", 0)
        }

        save_data(current_data, file_name)
        st.success(f"Đã thêm thành công '{new_word}' vào bộ sưu tập!")
        st.balloons()
