import re
import random
import streamlit as st
from utils.data_manager import load_data, save_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Study | Vocabulary Trainer", page_icon="📖", layout="wide")
apply_global_theme("1_Study")

# --- CUSTOM CSS: WARM EDITORIAL FLASHCARD ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 720px !important;
    }

    .study-header {
        text-align: center;
        margin-bottom: 1.2rem;
    }
    .study-sub {
        font-size: 0.85rem;
        font-weight: 600;
        color: #78716C;
        letter-spacing: 0.4px;
    }
    .study-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }

    /* Khung bao Flashcard kiểu thẻ bài Editorial */
    .flashcard-shell {
        background-color: #EFECE3;
        border: 1px solid #E5DFD2;
        border-radius: 24px;
        padding: 16px;
        margin-top: 10px;
        margin-bottom: 16px;
    }
    .flashcard-inner {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 18px;
        padding: 46px 24px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(28, 25, 23, 0.04);
    }

    .badge-colloc {
        display: inline-block;
        background-color: #EDE9FE;
        color: #7C3AED;
        border: 1px solid #DDD6FE;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
    }
    .badge-vocab {
        display: inline-block;
        background-color: #F3EFE6;
        color: #78716C;
        border: 1px solid #E7E2D6;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 12px;
    }
    .card-word {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        line-height: 1.2;
    }
    .card-hint {
        font-size: 0.82rem;
        color: #A8A29E;
        margin-top: 14px;
    }

    /* Pill thống kê nhỏ phía trên */
    .mini-stats {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #57534E;
    }
</style>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username

# --- 1. TẢI & GỘP DỮ LIỆU TỪ CẢ HAI KHO ---
vocab_file = f"data_vocab_{username}.json"
colloc_file = f"data_collocation_{username}.json"

vocab_data = load_data(vocab_file)
colloc_data = load_data(colloc_file)

if not isinstance(vocab_data, dict):
    vocab_data = {}
if not isinstance(colloc_data, dict):
    colloc_data = {}

combined_data = {}
word_source_map = {}

for w, info in vocab_data.items():
    combined_data[w] = info
    word_source_map[w] = "vocab"

for w, info in colloc_data.items():
    combined_data[w] = info
    word_source_map[w] = "colloc"

all_words = list(combined_data.keys())

st.markdown(f"""
<div class="study-header">
    <div class="study-sub">ACTIVE RECALL SESSION · {len(all_words)} WORDS IN VAULT</div>
    <div class="study-title">Study Vocabulary</div>
</div>
""", unsafe_allow_html=True)

if not all_words:
    st.info("Kho từ vựng của bạn hiện đang trống! Hãy sang mục Add Word hoặc Library để thêm từ nhé.")
    st.stop()

def is_collocation_item(word: str, info) -> bool:
    if word_source_map.get(word) == "colloc":
        return True
    if isinstance(info, dict):
        pos_val = str(info.get("pos", "")).lower()
        if "colloc" in pos_val or "phrase" in pos_val or "idiom" in pos_val:
            return True
    if len(word.strip().split()) >= 2:
        return True
    return False

# --- 2. TỰ ĐỘNG KHỞI TẠO LƯỢT HỌC NGAY KHI VÀO TRANG (MẶC ĐỊNH 20 TỪ) ---
if "study_batch_size" not in st.session_state:
    st.session_state.study_batch_size = 20

def start_new_batch(size_choice):
    if size_choice == "All":
        st.session_state.batch_words = all_words.copy()
        random.shuffle(st.session_state.batch_words)
    else:
        limit = min(int(size_choice), len(all_words))
        st.session_state.batch_words = random.sample(all_words, limit)
    st.session_state.studied_words = []
    if "current_word" in st.session_state:
        del st.session_state.current_word

if "batch_words" not in st.session_state:
    start_new_batch(st.session_state.study_batch_size)

if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

# --- 3. THANH ĐIỀU KHIỂN NHỎ GỌN PHÍA TRÊN (CHỌN SỐ LƯỢNG / LÀM MỚI) ---
c_size, c_shuffle = st.columns([2.2, 1])
with c_size:
    size_options = [10, 20, 50, "All"]
    selected_size = st.selectbox(
        "Session size",
        size_options,
        index=size_options.index(st.session_state.study_batch_size),
        label_visibility="collapsed"
    )
    if selected_size != st.session_state.study_batch_size:
        st.session_state.study_batch_size = selected_size
        start_new_batch(selected_size)
        st.rerun()

with c_shuffle:
    if st.button("New Session", use_container_width=True):
        start_new_batch(st.session_state.study_batch_size)
        st.rerun()

# Lọc danh sách từ còn lại
batch_list = [w for w in st.session_state.batch_words if w in combined_data]
remaining_words = [w for w in batch_list if w not in st.session_state.studied_words]

# --- 4. MÀN HÌNH HOÀN THÀNH LƯỢT HỌC ---
if not remaining_words:
    st.balloons()
    st.markdown(f"""
    <div class="flashcard-shell">
        <div class="flashcard-inner">
            <div class="badge-colloc">Session Complete</div>
            <div class="card-word" style="font-size:2rem;">You've reviewed {len(batch_list)} words!</div>
            <div class="card-hint">Great consistency. Keep building your long-term memory.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_r1, col_r2 = st.columns(2)
    with col_r1:
        if st.button("Review Same Batch", use_container_width=True):
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.rerun()
    with col_r2:
        if st.button("Start Next Batch  ↗", type="primary", use_container_width=True):
            start_new_batch(st.session_state.study_batch_size)
            st.rerun()
    st.stop()

# Chọn từ hiện tại
if ("current_word" not in st.session_state
    or st.session_state.current_word in st.session_state.studied_words
    or st.session_state.current_word not in remaining_words):
    st.session_state.current_word = random.choice(remaining_words)

current_word = st.session_state.current_word
word_info = combined_data[current_word]

# --- 5. THANH TIẾN ĐỘ & THẺ FLASHCARD ---
total_in_batch = len(batch_list)
studied_count = len(st.session_state.studied_words)
progress = studied_count / total_in_batch if total_in_batch > 0 else 0

st.markdown(f"""
<div class="mini-stats">
    <span>Progress: <b>{studied_count} / {total_in_batch}</b></span>
    <span>{round(progress * 100)}%</span>
</div>
""", unsafe_allow_html=True)
st.progress(progress)

badge_html = (
    '<div class="badge-colloc">Collocation</div>'
    if is_collocation_item(current_word, word_info)
    else '<div class="badge-vocab">Vocabulary</div>'
)

st.markdown(f"""
<div class="flashcard-shell">
    <div class="flashcard-inner">
        {badge_html}
        <div class="card-word">{current_word}</div>
        <div class="card-hint">Recall the Vietnamese meaning before revealing</div>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. SHOW MEANING & EXAMPLE ---
with st.expander("Show Meaning & Example", expanded=False, key=f"expander_{current_word}"):
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
        pos_tag = word_info.get("pos", "Other")
        example_text = word_info.get("example", "")

        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; margin-bottom: 10px;">
            <span style="font-size: 1.85rem; font-weight: 800; color: #1C1917; line-height: 1.2;">{meaning}</span>
            <span style="padding: 4px 12px; border-radius: 8px; font-size: 0.85rem; font-weight: 700; background-color: #EFECE3; color: #57534E; text-transform: uppercase; letter-spacing: 0.5px;">{pos_tag}</span>
        </div>
        """, unsafe_allow_html=True)

        if example_text:
            clean_ex = example_text.strip()
            if current_word.lower() in clean_ex.lower() and "<b>" not in clean_ex.lower():
                pattern = re.compile(re.escape(current_word), re.IGNORECASE)
                clean_ex = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", clean_ex)
            else:
                clean_ex = clean_ex.replace("**", "<b>", 1).replace("**", "</b>", 1)

            st.markdown(f"""
            <div style="border-top: 1px dashed #E7E2D6; padding-top: 12px; margin-top: 8px;">
                <div style="font-size: 1.15rem; color: #57534E; font-style: italic; line-height: 1.5;">
                    "{clean_ex}"
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        meaning = str(word_info)
        st.markdown(f'<div style="font-size: 1.85rem; font-weight: 800; color: #1C1917;">{meaning}</div>', unsafe_allow_html=True)

# --- 7. NÚT ĐÁNH GIÁ ---
st.write("")
col1, col2 = st.columns(2, gap="medium")

def handle_answer(is_correct):
    st.session_state.studied_words.append(current_word)

    source = word_source_map.get(current_word, "vocab")
    target_dict = colloc_data if source == "colloc" else vocab_data
    target_file = colloc_file if source == "colloc" else vocab_file

    if current_word in target_dict and isinstance(target_dict[current_word], dict):
        if "correct" not in target_dict[current_word]:
            target_dict[current_word]["correct"] = 0
        if "wrong" not in target_dict[current_word]:
            target_dict[current_word]["wrong"] = 0

        if is_correct:
            target_dict[current_word]["correct"] += 1
        else:
            target_dict[current_word]["wrong"] += 1

        save_data(target_dict, target_file)

with col1:
    if st.button("Still Learning", use_container_width=True, key=f"btn_wrong_{current_word}", type="secondary"):
        handle_answer(False)
        st.rerun()

with col2:
    if st.button("Got It  ✓", use_container_width=True, key=f"btn_correct_{current_word}", type="primary"):
        handle_answer(True)
        st.rerun()
