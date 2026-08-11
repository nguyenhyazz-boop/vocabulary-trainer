import random
import streamlit as st
from utils.data_manager import load_data, save_data

# =========================
# Cấu hình trang
# =========================
st.set_page_config(page_title="Study - Vocabulary Trainer", page_icon="📖", layout="wide")

st.markdown("""
    <style>
    .flashcard-box {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 18px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #EAE6DF;
        text-align: center;
        margin-bottom: 20px;
    }
    .card-label {
        font-size: 0.95rem;
        color: #8C8C8C;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .card-word {
        font-size: 2.2rem;
        font-weight: 700;
        color: #2D3142;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📖 Study Vocabulary")

# --- 1. ĐỌC DỮ LIỆU ---
data = load_data()

if not data:
    st.info("Chưa có từ vựng nào trong dữ liệu. Hãy sang trang 'Add Word' để thêm từ mới!")
    st.stop()

# Khởi tạo chế độ học mặc định trong session (Mặc định là Vocabulary Normal)
if "study_mode" not in st.session_state:
    st.session_state.study_mode = "vocab"

# --- 2. TẠO 2 NÚT BẤM LỰA CHỌN NỔI BẬT ---
st.write("📌 **Chọn nội dung bạn muốn học:**")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    type_normal = "primary" if st.session_state.study_mode == "vocab" else "secondary"
    if st.button("🔤 Normal Vocabulary", type=type_normal, use_container_width=True):
        st.session_state.study_mode = "vocab"
        st.rerun()

with col_btn2:
    type_colloc = "primary" if st.session_state.study_mode == "collocation" else "secondary"
    if st.button("🔗 Collocations & Phrases", type=type_colloc, use_container_width=True):
        st.session_state.study_mode = "collocation"
        st.rerun()

st.divider()

# --- 3. LỌC DANH SÁCH TỪ THEO NÚT BẤM ---
if st.session_state.study_mode == "collocation":
    all_words = [w for w in data.keys() if " " in w.strip()]
    mode_title = "🔗 Collocation & Phrase"
else:
    all_words = [w for w in data.keys() if " " not in w.strip()]
    mode_title = "🔤 Normal Vocabulary"

if not all_words:
    st.warning(f"Chưa có từ nào thuộc danh mục **{mode_title}**!")
    st.stop()

# --- 4. KHỞI TẠO TRẠNG THÁI KHÔNG LẶP TỪ ---
if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

# Lọc các từ chưa học trong chế độ hiện tại
remaining_words = [w for w in all_words if w not in st.session_state.studied_words]

# Khi đã học hết các từ trong chế độ này
if not remaining_words:
    st.balloons()
    st.success(f"🎉 Bạn đã học hết tất cả từ thuộc nhóm **{mode_title}** trong phiên này!")
    if st.button("🔄 Học lại nhóm này từ đầu", use_container_width=True):
        st.session_state.studied_words = [w for w in st.session_state.studied_words if w not in all_words]
        st.rerun()
    st.stop()

# Chọn từ mới
if ("current_word" not in st.session_state 
    or st.session_state.current_word in st.session_state.studied_words
    or st.session_state.current_word not in all_words):
    st.session_state.current_word = random.choice(remaining_words)

current_word = st.session_state.current_word

# --- 5. PROGRESS BAR & SỐ TỪ ĐÃ HỌC ---
total_words = len(all_words)
studied_count = len([w for w in all_words if w in st.session_state.studied_words])

progress = studied_count / total_words if total_words > 0 else 0
st.progress(progress)
st.caption(f"Tiến độ ({mode_title}): **{studied_count} / {total_words}** từ")

# --- 6. HIỂN THỊ TỪ VỰNG & SHOW MEANING ---
st.markdown(f"""
    <div class="flashcard-box">
        <div class="card-label">{mode_title}</div>
        <div class="card-word">{current_word}</div>
    </div>
""", unsafe_allow_html=True)

with st.expander("👀 Show Meaning", expanded=False, key=f"expander_{current_word}"):
    word_info = data[current_word]
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    else:
        meaning = str(word_info)
    
    st.markdown(f"### 👉 **{meaning}**")

# --- 7. NÚT CORRECT / WRONG & LƯU DATA.JSON ---
st.write("---")
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

        save_data(data)

with col1:
    if st.button("✅ Correct", use_container_width=True):
        handle_answer(True)
        st.rerun()

with col2:
    if st.button("❌ Wrong", use_container_width=True):
        handle_answer(False)
        st.rerun()
