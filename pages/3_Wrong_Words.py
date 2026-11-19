import re
import random
import streamlit as st
from utils.data_manager import load_data, save_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Error Clinic | Vocabulary Trainer", page_icon="📖", layout="wide")
apply_global_theme("3_Wrong_Words")

# --- CUSTOM CSS: WARM EDITORIAL ERROR CLINIC ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 820px !important;
    }

    .clinic-header {
        margin-bottom: 1.4rem;
    }
    .clinic-sub {
        font-size: 0.82rem;
        font-weight: 700;
        color: #78716C;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .clinic-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }

    /* Khung Drill phản xạ */
    .drill-shell {
        background-color: #EFECE3;
        border: 1px solid #E5DFD2;
        border-radius: 22px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .drill-inner {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 16px;
        padding: 32px 24px;
        text-align: center;
    }
    .drill-meaning {
        font-size: 1.85rem;
        font-weight: 800;
        color: #1C1917;
        margin: 8px 0;
    }
    .drill-context {
        font-size: 1.05rem;
        color: #57534E;
        font-style: italic;
        margin-top: 10px;
    }

    /* Thẻ từ sai */
    .error-card {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 16px;
        padding: 18px 20px;
        margin-bottom: 12px;
    }
    .badge-colloc {
        display: inline-block;
        background-color: #EDE9FE;
        color: #7C3AED;
        font-size: 0.7rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .badge-pos {
        display: inline-block;
        background-color: #F3EFE6;
        color: #57534E;
        font-size: 0.7rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }
    .badge-miss {
        display: inline-block;
        background-color: #FEE2E2;
        color: #DC2626;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
    }
    .err-word {
        font-size: 1.35rem;
        font-weight: 800;
        color: #1C1917;
        margin-top: 6px;
    }
    .err-meaning {
        font-size: 1rem;
        font-weight: 600;
        color: #44403C;
    }
    .err-example {
        font-size: 0.92rem;
        color: #78716C;
        font-style: italic;
        margin-top: 8px;
        padding-top: 8px;
        border-top: 1px dashed #E7E2D6;
    }
</style>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username

colloc_file = f"data_collocation_{username}.json"
vocab_file = f"data_vocab_{username}.json"

colloc_data = load_data(colloc_file)
vocab_data = load_data(vocab_file)

if not isinstance(colloc_data, dict):
    colloc_data = {}
if not isinstance(vocab_data, dict):
    vocab_data = {}

# Gộp dữ liệu nhưng KHÔNG ghi đè field phụ vào dict gốc để tránh làm bẩn JSON
wrong_items = {}
for w, item in vocab_data.items():
    if isinstance(item, dict) and item.get("wrong", 0) > 0:
        wrong_items[w] = {**item, "_source_file": vocab_file, "_is_colloc": len(w.split()) >= 2}

for w, item in colloc_data.items():
    if isinstance(item, dict) and item.get("wrong", 0) > 0:
        wrong_items[w] = {**item, "_source_file": colloc_file, "_is_colloc": True}

st.markdown("""
<div class="clinic-header">
    <div class="clinic-sub">Targeted Error Recovery</div>
    <div class="clinic-title">Error Clinic</div>
</div>
""", unsafe_allow_html=True)

# --- TRẠNG THÁI SẠCH LỖI (ZERO ERRORS) ---
if not wrong_items:
    st.markdown("""
    <div class="drill-shell">
        <div class="drill-inner">
            <div class="badge-colloc" style="margin-bottom:10px;">Clean Record</div>
            <div class="drill-meaning">Zero Missed Words</div>
            <div style="font-size:0.95rem; color:#78716C; max-width:440px; margin:0 auto 18px auto; line-height:1.5;">
                Kho từ vựng của bạn hiện không có từ nào bị đánh dấu sai. Tiếp tục luyện tập để duy trì độ chính xác nhé!
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    c_go1, c_go2 = st.columns(2)
    with c_go1:
        if st.button("Open Study Flashcards  ↗", type="primary", use_container_width=True):
            st.switch_page("pages/1_Study.py")
    with c_go2:
        if st.button("View Retention Analytics", use_container_width=True):
            st.switch_page("pages/2_Statistics.py")
    st.stop()

# --- HÀM CẬP NHẬT ĐIỂM SAI VÀO FILE GỐC ---
def clear_word_error(word: str, target_file: str, mode: str = "reset"):
    file_data = load_data(target_file)
    if word in file_data and isinstance(file_data[word], dict):
        if mode == "reset":
            file_data[word]["wrong"] = 0
        elif mode == "decrement":
            file_data[word]["wrong"] = max(0, file_data[word].get("wrong", 1) - 1)
            file_data[word]["correct"] = file_data[word].get("correct", 0) + 1
        save_data(file_data, target_file)

# --- CHIA 2 TAB: PHẢN XẠ SỬA LỖI & SỔ ĐEN CHI TIẾT ---
tab_drill, tab_list = st.tabs([
    f"Quick Error Drill ({len(wrong_items)})",
    f"Error Log ({len(wrong_items)})"
])

# ==============================================================================
# TAB 1: PHẢN XẠ GÕ TỪ ĐỂ GỠ LỖI
# ==============================================================================
with tab_drill:
    wrong_keys = list(wrong_items.keys())
    if "drill_word" not in st.session_state or st.session_state.drill_word not in wrong_keys:
        st.session_state.drill_word = random.choice(wrong_keys)

    d_word = st.session_state.drill_word
    d_info = wrong_items[d_word]
    d_meaning = d_info.get("meaning", d_info.get("definition", ""))
    d_pos = d_info.get("pos", "Other")
    d_ex = d_info.get("example", "").strip()
    d_wrong = d_info.get("wrong", 1)

    # Che từ cần điền trong câu ví dụ nếu có
    masked_ex = ""
    if d_ex:
        clean_ex = re.sub(r"</?b>|\*\*", "", d_ex)
        pattern = re.compile(re.escape(d_word), re.IGNORECASE)
        masked_ex = pattern.sub("________", clean_ex)

    badge_html = (
        '<span class="badge-colloc">Collocation</span>'
        if d_info.get("_is_colloc")
        else f'<span class="badge-pos">{d_pos}</span>'
    )

    st.markdown(f"""
    <div class="drill-shell">
        <div class="drill-inner">
            <div style="display:flex; justify-content:center; gap:8px; margin-bottom:8px;">
                {badge_html}
                <span class="badge-miss">{d_wrong} missed</span>
            </div>
            <div class="drill-meaning">{d_meaning}</div>
            {f'<div class="drill-context">"{masked_ex}"</div>' if masked_ex else ''}
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form(key=f"drill_form_{d_word}", clear_on_submit=True):
        user_guess = st.text_input(
            "Type the English word or phrase",
            placeholder="Enter exact spelling to clear 1 error point...",
            label_visibility="collapsed"
        )
        c_sub1, c_sub2 = st.columns([2, 1])
        with c_sub1:
            submitted = st.form_submit_button("Check & Clear Error  ↗", type="primary", use_container_width=True)
        with c_sub2:
            skipped = st.form_submit_button("Skip Word", use_container_width=True)

        if submitted:
            if user_guess.strip().lower() == d_word.strip().lower():
                clear_word_error(d_word, d_info["_source_file"], mode="decrement")
                st.toast(f"Chính xác! Đã giảm điểm sai cho '{d_word}'.")
                if "drill_word" in st.session_state:
                    del st.session_state.drill_word
                st.rerun()
            else:
                st.error(f"Chưa chính xác! Đáp án đúng là: **{d_word}**")

        if skipped:
            others = [w for w in wrong_keys if w != d_word]
            st.session_state.drill_word = random.choice(others) if others else d_word
            st.rerun()

# ==============================================================================
# TAB 2: DANH SÁCH TỪ SAI CHI TIẾT
# ==============================================================================
with tab_list:
    top_bar1, top_bar2 = st.columns([2.2, 1])
    with top_bar1:
        st.caption(f"Đang có **{len(wrong_items)}** từ cần củng cố trí nhớ.")
    with top_bar2:
        if st.button("Practice All in Study  ↗", type="primary", use_container_width=True):
            st.session_state.batch_words = list(wrong_items.keys())
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.switch_page("pages/1_Study.py")

    st.write("")

    sorted_wrong = sorted(wrong_items.items(), key=lambda x: x[1].get("wrong", 0), reverse=True)

    for word, item in sorted_wrong:
        meaning = item.get("meaning", item.get("definition", ""))
        pos_tag = item.get("pos", "Other")
        wrong_cnt = item.get("wrong", 0)
        correct_cnt = item.get("correct", 0)
        example_text = item.get("example", "").strip()
        target_file = item["_source_file"]

        c_card, c_act = st.columns([3.3, 1], gap="medium")

        with c_card:
            type_badge = (
                '<span class="badge-colloc">Collocation</span>'
                if item.get("_is_colloc")
                else f'<span class="badge-pos">{pos_tag}</span>'
            )
            ex_html = ""
            if example_text:
                clean_ex = example_text
                if word.lower() in clean_ex.lower() and "<b>" not in clean_ex.lower():
                    pattern = re.compile(re.escape(word), re.IGNORECASE)
                    clean_ex = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", clean_ex)
                ex_html = f'<div class="err-example">"{clean_ex}"</div>'

            st.markdown(f"""
            <div class="error-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>{type_badge}</div>
                    <span class="badge-miss">{wrong_cnt} wrong · {correct_cnt} correct</span>
                </div>
                <div class="err-word">{word}</div>
                <div class="err-meaning">{meaning}</div>
                {ex_html}
            </div>
            """, unsafe_allow_html=True)

        with c_act:
            st.write("")
            st.write("")
            if st.button("Mark Mastered", key=f"fixed_{word}", use_container_width=True):
                clear_word_error(word, target_file, mode="reset")
                st.toast(f"Đã xóa '{word}' khỏi sổ đen!")
                st.rerun()
