import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Add Word | Vocabulary Trainer", page_icon="📝", layout="wide")

# --- CUSTOM CSS: NÂNG CAP GIAO DIỆN CHUẨN MODERN SAAS ---
st.markdown("""
<style>
    /* Tổng thể font & padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1000px;
    }
    
    /* Header tối giản */
    .app-header {
        margin-bottom: 2rem;
    }
    .app-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
    }

    /* Thẻ Container xem trước (Live Preview Card) */
    .preview-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    .preview-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
    }
    .preview-word {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    
    /* Badge loại từ phong cách Notion */
    .pos-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-noun { background-color: #E0F2FE; color: #0369A1; }
    .badge-verb { background-color: #DCFCE7; color: #15803D; }
    .badge-adj { background-color: #FEF9C3; color: #A16207; }
    .badge-adv { background-color: #F3E8FF; color: #7E22CE; }
    .badge-phrase { background-color: #FFEDD5; color: #C2410C; }
    .badge-other { background-color: #F1F5F9; color: #475569; }

    .preview-meaning {
        font-size: 1.1rem;
        color: #334155;
        margin-top: 12px;
        font-weight: 500;
    }
    .preview-example {
        font-size: 0.9rem;
        color: #64748B;
        font-style: italic;
        margin-top: 8px;
        padding-left: 10px;
        border-left: 2px solid #CBD5E1;
    }
</style>
""", unsafe_allow_html=True)

# --- GIỚI THIỆU HEADER ---
st.markdown("""
<div class="app-header">
    <div class="app-title">Add New Word</div>
    <div class="app-subtitle">Thêm và phân loại từ vựng mới vào bộ sưu tập cá nhân của bạn</div>
</div>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

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

# --- CHIA 2 CỘT: CỘT NHẬP FORM & CỘT LIVE PREVIEW ---
col_form, col_preview = st.columns([3, 2], gap="large")

with col_form:
    st.subheader("Thông tin từ vựng")
    
    new_word = st.text_input("Từ / Cụm từ Tiếng Anh", placeholder="e.g. permanent, take action").strip()
    
    col_pos, col_repo = st.columns(2)
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
    
    new_meaning = st.text_input("Nghĩa Tiếng Việt", placeholder="e.g. vĩnh viễn, lâu dài").strip()
    example_sentence = st.text_area("Câu ví dụ (Không bắt buộc)", placeholder="e.g. They are looking for a permanent solution.", height=80).strip()

    st.write("")
    submitted = st.button("Lưu Từ Vựng", type="primary", use_container_width=True)

# --- CỘT LIVE PREVIEW (XEM TRƯỚC THẺ TỪ) ---
with col_preview:
    st.subheader("Xem trước thẻ từ")
    
    # Xác định class badge màu sắc
    pos_short = word_pos.split(" ")[0].lower()
    badge_class = f"badge-{pos_short}" if pos_short in ["noun", "verb", "adj", "adv", "phrase"] else "badge-other"
    
    display_word = new_word if new_word else "Word Preview"
    display_meaning = new_meaning if new_meaning else "Nghĩa của từ sẽ hiển thị ở đây..."
    display_example = example_sentence if example_sentence else "Câu ví dụ minh họa sẽ hiển thị ở đây..."

    # Render HTML Card
    st.markdown(f"""
    <div class="preview-card">
        <div>
            <span class="preview-word">{display_word}</span>
            <span class="pos-badge {badge_class}" style="margin-left: 8px;">{word_pos.split(' ')[0]}</span>
        </div>
        <div class="preview-meaning">{display_meaning}</div>
        <div class="preview-example">"{display_example}"</div>
    </div>
    """, unsafe_allow_html=True)

# --- XỬ LÝ LƯU DỮ LIỆU ---
if submitted:
    if not new_word or not new_meaning:
        st.error("❌ Vui lòng nhập đầy đủ Từ tiếng Anh và Nghĩa tiếng Việt!")
    else:
        word_key = new_word.lower()
        pos_code = word_pos.split(" ")[0]

        current_data[word_key] = {
            "meaning": new_meaning,
            "pos": pos_code,
            "example": example_sentence,
            "correct": current_data.get(word_key, {}).get("correct", 0),
            "wrong": current_data.get(word_key, {}).get("wrong", 0)
        }

        save_data(current_data, file_name)
        st.success(f"🎉 Đã thêm thành công **{new_word}** vào bộ sưu tập!")
        st.balloons()
