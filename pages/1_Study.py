import random
import streamlit as st
from utils.data_manager import load_data, save_data

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

# Kiểm tra trạng thái đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

if "study_mode" not in st.session_state:
    st.session_state.study_mode = "collocation"

# --- 1. CHỌN KHO TỪ VỰNG ---
st.write("📌 **Chọn kho từ vựng bạn muốn học:**")
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    type_colloc = "primary" if st.session_state.study_mode == "collocation" else "secondary"
    if st.button("🔗 Collocations", type=type_colloc, use_container_width=True, key="study_btn_colloc"):
        st.session_state.study_mode = "collocation"
        st.rerun()

with col_btn2:
    type_normal = "primary" if st.session_state.study_mode == "vocab" else "secondary"
    if st.button("🔤 Normal Vocabulary", type=type_normal, use_container_width=True, key="study_btn_vocab"):
        st.session_state.study_mode = "vocab"
        st.rerun()

st.divider()

# --- 2. XÁC ĐỊNH FILE DỮ LIỆU CÁ NHÂN ---
if st.session_state.study_mode == "vocab":
    data_file = f"data_vocab_{username}.json"
    mode_title = "🔤 Normal Vocabulary"
else:
    data_file = f"data_collocation_{username}.json"
    mode_title = "🔗 Collocations & Phrases"

data = load_data(data_file)
all_words = list(data.keys())

if not all_words:
    st.info(f"Kho **{mode_title}** của bạn hiện đang trống! Hãy sang mục **Library** để chọn thêm từ vào nhé.")
    st.stop()

# --- 3. QUẢN LÝ TẬP TỪ ĐÃ HỌC ---
if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

remaining_words = [w for w in all_words if w not in st.session_state.studied_words]

if not remaining_words:
    st.balloons()
    st.success(f"🎉 Bạn đã hoàn thành toàn bộ từ vựng trong kho **{mode_title}**!")
    if st.button("🔄 Học lại kho này từ đầu", use_container_width=True, key="reset_study_btn"):
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
st.caption(f"Tiến độ kho ({mode_title}): **{studied_count} / {total_words}** từ")

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
        pos_tag = word_info.get("pos", "")
        topic_tag = word_info.get("topic", "")
        
        st.markdown(f"### 👉 **{meaning}**")
        
        info_list = []
        if pos_tag:
            info_list.append(f"Loại từ: **{pos_tag}**")
        if topic_tag:
            info_list.append(f"Chủ đề: **{topic_tag}**")
            
        if info_list:
            st.caption(" ┆ ".join(info_list))
    else:
        meaning = str(word_info)
        st.markdown(f"### 👉 **{meaning}**")

# --- 5. LƯU KẾT QUẢ VÀ NÚT BẤM (GÁN KEY ĐỘNG TRÁNH LỖI TRÙNG ID) ---
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

        save_data(data, data_file)

with col1:
    if st.button("✅ Correct", use_container_width=True, key=f"btn_correct_{current_word}"):
        handle_answer(True)
        st.rerun()

with col2:
    if st.button("❌ Wrong", use_container_width=True, key=f"btn_wrong_{current_word}"):
        handle_answer(False)
        st.rerun()
with col2:
    if st.button("❌ Wrong", use_container_width=True):
        handle_answer(False)
        st.rerun()
