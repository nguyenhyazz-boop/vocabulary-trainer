import random
import streamlit as st
from utils.data_manager import load_data, save_data

# =========================
# Cấu hình trang
# =========================
st.set_page_config(page_title="Study - Vocabulary Trainer", page_icon="📖", layout="wide")

# Custom CSS cho khung Flashcard chill
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
all_words = list(data.keys())

if not all_words:
    st.info("Chưa có từ vựng nào trong dữ liệu. Hãy sang trang 'Add Word' để thêm từ mới!")
    st.stop()

# --- 2. KHỞI TẠO TRẠNG THÁI KHÔNG LẶP TỪ ---
if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

# Lọc ra các từ chưa học trong phiên hiện tại
remaining_words = [w for w in all_words if w not in st.session_state.studied_words]

# Khi đã học hết tất cả các từ trong file
if not remaining_words:
    st.balloons()
    st.success("🎉 Bạn đã học hết tất cả các từ trong phiên này!")
    if st.button("🔄 Học lại từ đầu", use_container_width=True):
        st.session_state.studied_words = []
        st.rerun()
    st.stop()

# Chọn từ mới nếu chưa có từ hiện tại hoặc từ hiện tại vừa được bấm trả lời
if "current_word" not in st.session_state or st.session_state.current_word in st.session_state.studied_words:
    st.session_state.current_word = random.choice(remaining_words)

current_word = st.session_state.current_word

# --- 3. PROGRESS BAR & SỐ TỪ ĐÃ HỌC ---
total_words = len(all_words)
studied_count = len(st.session_state.studied_words)

progress = studied_count / total_words if total_words > 0 else 0
st.progress(progress)
st.caption(f"Số từ đã học trong phiên: **{studied_count} / {total_words}** từ")

# --- 4. HIỂN THỊ TỪ VỰNG & SHOW MEANING ---
st.divider()

# Khung hiển thị từ vựng phong cách Flashcard
st.markdown(f"""
    <div class="flashcard-box">
        <div class="card-label">Current Word</div>
        <div class="card-word">{current_word}</div>
    </div>
""", unsafe_allow_html=True)

# Sử dụng key động theo tên từ vựng để ép Streamlit reset expander về trạng thái đóng khi đổi từ
with st.expander("👀 Show Meaning", expanded=False, key=f"expander_{current_word}"):
    word_info = data[current_word]
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    else:
        meaning = str(word_info)
    
    st.markdown(f"### 👉 **{meaning}**")

# --- 5. NÚT CORRECT / WRONG & TỰ LƯU DATA.JSON ---
st.write("---")
col1, col2 = st.columns(2)


def handle_answer(is_correct):
    # Đánh dấu từ đã học
    st.session_state.studied_words.append(current_word)

    # Cập nhật số lần đúng/sai vào data.json
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
