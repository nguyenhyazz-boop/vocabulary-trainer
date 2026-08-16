import re
import random
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Study | Vocabulary Trainer", page_icon="📖", layout="wide")

# --- CUSTOM CSS: BÓP HẸP KHUNG CHO VỪA MẮT & NỔI BẬT KHỐI NỘI DUNG ---
st.markdown("""
<style>
    /* Bóp chiều rộng tổng thể về chuẩn kích thước Flashcard UI */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 680px !important;
    }
    
    .app-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
        margin-bottom: 0.5rem;
        text-align: center;
    }

    .flashcard-box {
        background-color: #FFFFFF;
        padding: 40px 20px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03);
        border: 1px solid #E2E8F0;
        text-align: center;
        margin-bottom: 16px;
    }
    .card-label {
        font-size: 0.75rem;
        font-weight: 600;
        color: #94A3B8;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .card-word {
        font-size: 2.4rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 8px;
    }

    /* Khối ví dụ lấp đầy card */
    .example-block {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-top: 14px;
        text-align: left;
    }
    .example-title {
        font-size: 0.75rem;
        font-weight: 700;
        color: #94A3B8;
        text-transform: uppercase;
        margin-bottom: 6px;
        letter-spacing: 0.5px;
    }
    .example-content {
        font-size: 1.15rem;
        color: #334155;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">Study Vocabulary</div>', unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

if "study_mode" not in st.session_state:
    st.session_state.study_mode = "collocation"

# --- 1. CHỌN KHO TỪ VỰNG ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    type_colloc = "primary" if st.session_state.study_mode == "collocation" else "secondary"
    if st.button("Collocations", type=type_colloc, use_container_width=True, key="study_btn_colloc"):
        st.session_state.study_mode = "collocation"
        st.rerun()

with col_btn2:
    type_normal = "primary" if st.session_state.study_mode == "vocab" else "secondary"
    if st.button("Normal Vocabulary", type=type_normal, use_container_width=True, key="study_btn_vocab"):
        st.session_state.study_mode = "vocab"
        st.rerun()

st.write("")

# --- 2. XÁC ĐỊNH FILE DỮ LIỆU CÁ NHÂN ---
if st.session_state.study_mode == "vocab":
    data_file = f"data_vocab_{username}.json"
    mode_title = "Normal Vocabulary"
else:
    data_file = f"data_collocation_{username}.json"
    mode_title = "Collocations & Phrases"

data = load_data(data_file)
all_words = list(data.keys())

if not all_words:
    st.info(f"Kho **{mode_title}** của bạn hiện đang trống! Hãy sang mục Add Word hoặc Library để thêm từ nhé.")
    st.stop()

# --- 3. QUẢN LÝ TẬP TỪ ĐÃ HỌC ---
if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

remaining_words = [w for w in all_words if w not in st.session_state.studied_words]

if not remaining_words:
    st.balloons()
    st.success(f"Bạn đã hoàn thành toàn bộ từ vựng trong kho **{mode_title}**!")
    if st.button("Học lại kho này từ đầu", use_container_width=True, key="reset_study_btn"):
        st.session_state.studied_words = [w for w in st.session_state.studied_words if w not in all_words]
        st.rerun()
    st.stop()

if ("current_word" not in st.session_state 
    or st.session_state.current_word in st.session_state.studied_words
    or st.session_state.current_word not in all_words):
    st.session_state.current_word = random.choice(remaining_words)

current_word = st.session_state.current_word

# --- 4. HIỂN THỊ TỪ VỰNG (FLASHCARD) ---
total_words = len(all_words)
studied_count = len([w for w in all_words if w in st.session_state.studied_words])

progress = studied_count / total_words if total_words > 0 else 0
st.progress(progress)
st.caption(f"Tiến độ kho: **{studied_count} / {total_words}** từ")

st.markdown(f"""
    <div class="flashcard-box">
        <div class="card-label">{mode_title}</div>
        <div class="card-word">{current_word}</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. SHOW MEANING & EXAMPLE (THIẾT KẾ ĐẦY ĐẶN BẢO BỌC) ---
with st.expander("Show Meaning & Example", expanded=False, key=f"expander_{current_word}"):
    word_info = data[current_word]
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
        pos_tag = word_info.get("pos", "Other")
        example_text = word_info.get("example", "")
        
        # Hàng 1: Nghĩa to & Tag loại từ nằm sát nhau
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <span style="font-size: 1.5rem; font-weight: 700; color: #0F172A;">{meaning}</span>
            <span class="pos-badge badge-other" style="padding: 3px 8px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; background-color: #F1F5F9; color: #475569;">{pos_tag}</span>
        </div>
        """, unsafe_allow_html=True)

        # Hàng 2: Khối câu ví dụ nổi bật ôm trọn nội dung
        if example_text:
            clean_ex = example_text.strip()
            
            # Tự động chuyển Markdown **word** sang thẻ <b>word</b> để rendered mượt trong HTML
            if current_word.lower() in clean_ex.lower() and "<b>" not in clean_ex.lower():
                pattern = re.compile(re.escape(current_word), re.IGNORECASE)
                clean_ex = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", clean_ex)
            else:
                clean_ex = clean_ex.replace("**", "<b>", 1).replace("**", "</b>", 1)

            st.markdown(f"""
            <div class="example-block">
                <div class="example-title">Example</div>
                <div class="example-content">"{clean_ex}"</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        meaning = str(word_info)
        st.markdown(f'<div style="font-size: 1.4rem; font-weight: 700; color: #0F172A;">{meaning}</div>', unsafe_allow_html=True)

# --- 6. NÚT ĐÁNH GIÁ ---
st.write("")
col1, col2 = st.columns(2)

def handle_answer(is_correct):
    st.session_state.studied_words.append(current_word)

    if isinstance(data[current_word], dict):
        if "correct" not in data[current_word]:
            data[current_word]["correct"] = 0
        if "wrong" not in data[current_word]:
            data[current_word]["wrong"] = 0

        if is_correct:
            data[current_word]["correct"] += 1
        else:
            data[current_word]["wrong"] += 1

        save_data(data, data_file)

with col1:
    if st.button("Correct", use_container_width=True, key=f"btn_correct_{current_word}", type="primary"):
        handle_answer(True)
        st.rerun()

with col2:
    if st.button("Wrong", use_container_width=True, key=f"btn_wrong_{current_word}", type="secondary"):
        handle_answer(False)
        st.rerun()
