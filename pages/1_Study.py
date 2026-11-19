import re
import random
import streamlit as st
from utils.data_manager import load_data, save_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Study | Vocabulary Trainer", page_icon="📖", layout="wide")
apply_global_theme("1_Study")

# --- CUSTOM CSS: FLASHCARD WARM EDITORIAL ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 680px !important;
    }
    
    .app-title {
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #1C1917;
        letter-spacing: -0.5px;
        margin-bottom: 1.2rem;
        text-align: center;
    }

    .flashcard-box {
        background-color: #FFFFFF;
        padding: 42px 24px;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(28, 25, 23, 0.04);
        border: 1px solid #E7E2D6;
        text-align: center;
        margin-bottom: 16px;
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
        margin-bottom: 10px;
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
        margin-bottom: 10px;
    }
    .card-word {
        font-size: 2.45rem;
        font-weight: 800;
        color: #1C1917;
        margin-top: 4px;
        letter-spacing: -0.5px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">Study Vocabulary</div>', unsafe_allow_html=True)

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

# Tạo từ điển hợp nhất & ghi nhớ nguồn gốc từng từ để lưu điểm chính xác
combined_data = {}
word_source_map = {}  # Lưu ("colloc" hoặc "vocab") cho từng từ

for w, info in vocab_data.items():
    combined_data[w] = info
    word_source_map[w] = "vocab"

for w, info in colloc_data.items():
    combined_data[w] = info
    word_source_map[w] = "colloc"

all_words = list(combined_data.keys())

if not all_words:
    st.info("Kho từ vựng của bạn hiện đang trống! Hãy sang mục Add Word hoặc Library để thêm từ nhé.")
    st.stop()

# Hàm kiểm tra một từ có phải Collocation / cụm từ hay không
def is_collocation_item(word: str, info) -> bool:
    if word_source_map.get(word) == "colloc":
        return True
    if isinstance(info, dict):
        pos_val = str(info.get("pos", "")).lower()
        if "colloc" in pos_val or "phrase" in pos_val or "idiom" in pos_val:
            return True
    # Tự động nhận diện cụm từ (từ 2 chữ tiếng Anh trở lên)
    if len(word.strip().split()) >= 2:
        return True
    return False

# --- 2. BỘ CHỌN SỐ LƯỢNG TỪ CHO LƯỢT HỌC ---
if "batch_words" not in st.session_state:
    with st.container(border=True):
        st.markdown("#### Chọn kích thước lượt học")
        st.caption(f"Kho của bạn đang có tổng cộng **{len(all_words)}** từ & cụm từ.")
        
        batch_size = st.selectbox(
            "Bạn muốn học bao nhiêu từ trong lượt này?",
            [10, 20, 25, 50, "Tất cả"],
            index=1
        )
        
        st.write("")
        if st.button("Bắt đầu lượt học mới  ↗", type="primary", use_container_width=True):
            if batch_size != "Tất cả":
                limit = min(int(batch_size), len(all_words))
                st.session_state.batch_words = random.sample(all_words, limit)
            else:
                st.session_state.batch_words = all_words.copy()
                
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.rerun()
    st.stop()

# --- 3. QUẢN LÝ TẬP TỪ ĐÃ HỌC TRONG BATCH ---
if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

# Lọc các từ vẫn còn tồn tại trong kho
batch_list = [w for w in st.session_state.batch_words if w in combined_data]
remaining_words = [w for w in batch_list if w not in st.session_state.studied_words]

# Khi hoàn thành hết từ trong lượt
if not remaining_words:
    st.balloons()
    st.success(f"Hoàn thành xuất sắc lượt học ({len(batch_list)} từ)!")
    
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        if st.button("Học lại lượt vừa nãy", type="primary", use_container_width=True):
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.rerun()
    with col_r2:
        if st.button("Học lượt mới", use_container_width=True):
            del st.session_state.batch_words
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.rerun()
    with col_r3:
        if st.button("Chọn lại số từ", use_container_width=True):
            del st.session_state.batch_words
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.rerun()
    st.stop()

# Đảm bảo gán current_word an toàn
if ("current_word" not in st.session_state 
    or st.session_state.current_word in st.session_state.studied_words
    or st.session_state.current_word not in remaining_words):
    st.session_state.current_word = random.choice(remaining_words)

current_word = st.session_state.current_word
word_info = combined_data[current_word]

# --- 4. HIỂN THỊ TỪ VỰNG (FLASHCARD) & TIẾN ĐỘ ---
total_in_batch = len(batch_list)
studied_count = len(st.session_state.studied_words)

progress = studied_count / total_in_batch if total_in_batch > 0 else 0
st.progress(progress)

col_info1, col_info2 = st.columns([2.5, 1])
with col_info1:
    st.caption(f"Tiến độ lượt này: **{studied_count} / {total_in_batch}** từ")
with col_info2:
    if st.button("Đổi lượt học", help="Hủy lượt này để chọn lại số từ", use_container_width=True):
        del st.session_state.batch_words
        if "current_word" in st.session_state:
            del st.session_state.current_word
        st.rerun()

# Gắn badge chú thích Collocation nếu là cụm từ
if is_collocation_item(current_word, word_info):
    badge_html = '<div class="badge-colloc">Collocation</div>'
else:
    badge_html = '<div class="badge-vocab">Vocabulary</div>'

st.markdown(f"""
    <div class="flashcard-box">
        {badge_html}
        <div class="card-word">{current_word}</div>
    </div>
""", unsafe_allow_html=True)

# --- 5. SHOW MEANING & EXAMPLE ---
with st.expander("Show Meaning & Example", expanded=False, key=f"expander_{current_word}"):
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
        pos_tag = word_info.get("pos", "Other")
        example_text = word_info.get("example", "")
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 6px; margin-bottom: 12px;">
            <span style="font-size: 2rem; font-weight: 800; color: #1C1917; line-height: 1.2;">{meaning}</span>
            <span style="padding: 5px 12px; border-radius: 8px; font-size: 0.9rem; font-weight: 700; background-color: #EFECE3; color: #57534E; text-transform: uppercase; letter-spacing: 0.5px;">{pos_tag}</span>
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
            <div style="border-top: 1px dashed #E7E2D6; padding-top: 14px; margin-top: 10px;">
                <div style="font-size: 1.25rem; color: #57534E; font-style: italic; line-height: 1.5;">
                    "{clean_ex}"
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        meaning = str(word_info)
        st.markdown(f'<div style="font-size: 2rem; font-weight: 800; color: #1C1917;">{meaning}</div>', unsafe_allow_html=True)

# --- 6. NÚT ĐÁNH GIÁ ---
st.write("")
col1, col2 = st.columns(2)

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
    if st.button("Correct", use_container_width=True, key=f"btn_correct_{current_word}", type="primary"):
        handle_answer(True)
        st.rerun()

with col2:
    if st.button("Wrong", use_container_width=True, key=f"btn_wrong_{current_word}", type="secondary"):
        handle_answer(False)
        st.rerun()
