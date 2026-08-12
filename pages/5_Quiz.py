import random
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Quiz Arena - Vocabulary Trainer", page_icon="⚡", layout="wide")

# CSS tạo giao diện hiện đại & sinh động
st.markdown("""
    <style>
    .quiz-card {
        background: linear-gradient(135deg, #6B73FF 0%, #000DFF 100%);
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(107, 115, 255, 0.3);
        text-align: center;
        color: white;
        margin-bottom: 25px;
    }
    .quiz-tag {
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        opacity: 0.85;
    }
    .quiz-word {
        font-size: 2.8rem;
        font-weight: 800;
        margin-top: 10px;
        margin-bottom: 5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .quiz-pos {
        font-size: 1.1rem;
        font-style: italic;
        opacity: 0.9;
    }
    .streak-badge {
        background-color: #FF9F43;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.1rem;
        display: inline-block;
        box-shadow: 0 4px 10px rgba(255, 159, 67, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Khởi tạo Streak & Điểm số
if "streak" not in st.session_state:
    st.session_state.streak = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = "collocation"

# --- THANH TIÊU ĐỀ & KHOẢN ĐIỂM STREAK ---
head_col1, head_col2 = st.columns([2, 1])
with head_col1:
    st.title("⚡ Quiz Arena")
    st.caption("Thử thách phản xạ và kiểm tra trí nhớ từ vựng!")

with head_col2:
    st.write("")
    st.markdown(f"""
        <div style="text-align: right;">
            <span class="streak-badge">🔥 Streak: {st.session_state.streak} | 🏆 Điểm: {st.session_state.score}</span>
        </div>
    """, unsafe_allow_html=True)

st.write("")

# --- 1. CHỌN KHO TỪ VỰNG ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    type_colloc = "primary" if st.session_state.quiz_mode == "collocation" else "secondary"
    if st.button("🔗 Collocations Quiz", type=type_colloc, use_container_width=True):
        st.session_state.quiz_mode = "collocation"
        if "quiz_word" in st.session_state:
            del st.session_state.quiz_word
        st.rerun()

with col_btn2:
    type_normal = "primary" if st.session_state.quiz_mode == "vocab" else "secondary"
    if st.button("🔤 Normal Vocab Quiz", type=type_normal, use_container_width=True):
        st.session_state.quiz_mode = "vocab"
        if "quiz_word" in st.session_state:
            del st.session_state.quiz_word
        st.rerun()

st.divider()

# --- 2. XÁC ĐỊNH FILE DỮ LIỆU CÁ NHÂN ---
if st.session_state.quiz_mode == "vocab":
    data_file = f"data_vocab_{username}.json"
    mode_title = "Normal Vocabulary"
else:
    data_file = f"data_collocation_{username}.json"
    mode_title = "Collocations & Phrases"

data = load_data(data_file)
all_words = list(data.keys())

if not all_words:
    st.info(f"Kho **{mode_title}** của bạn hiện đang trống! Hãy sang **Library** để chọn thêm từ vào bộ học nhé.")
    st.stop()

# --- 3. CHỌN TỪ VỰNG NGẪU NHIÊN ---
if "quiz_word" not in st.session_state or st.session_state.quiz_word not in all_words:
    st.session_state.quiz_word = random.choice(all_words)
    st.session_state.answered = False

target_word = st.session_state.quiz_word
word_info = data[target_word]

if isinstance(word_info, dict):
    correct_meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    pos_tag = word_info.get("pos", "")
else:
    correct_meaning = str(word_info)
    pos_tag = ""

# --- 4. TẠO 4 ĐÁP ÁN TRẮC NGHIỆM ---
if "options" not in st.session_state or st.session_state.get("current_target") != target_word:
    other_meanings = []
    for w, item in data.items():
        if w != target_word:
            m = item.get("meaning", str(item)) if isinstance(item, dict) else str(item)
            if m not in other_meanings:
                other_meanings.append(m)
    
    default_fakes = ["nghiên cứu kỹ lưỡng", "tạo ra sự khác biệt", "chuẩn bị hành lý", "giữ liên lạc", "thực hiện kế hoạch"]
    for f in default_fakes:
        if len(other_meanings) < 3 and f != correct_meaning:
            other_meanings.append(f)

    selected_fakes = random.sample(other_meanings, min(3, len(other_meanings)))
    opts = selected_fakes + [correct_meaning]
    random.shuffle(opts)
    
    st.session_state.options = opts
    st.session_state.current_target = target_word

# --- 5. HIỂN THỊ THẺ BÀI QUIZ ---
pos_str = f"({pos_tag})" if pos_tag else ""
st.markdown(f"""
    <div class="quiz-card">
        <div class="quiz-tag">🎯 {mode_title}</div>
        <div class="quiz-word">{target_word}</div>
        <div class="quiz-pos">{pos_str}</div>
    </div>
""", unsafe_allow_html=True)

st.write("👉 **Chọn nghĩa tiếng Việt chính xác:**")

# --- 6. HIỂN THỊ NÚT BẤM ĐÁP ÁN DẠNG GRID 2x2 ---
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)

grid_cols = [row1_col1, row1_col2, row2_col1, row2_col2]

def check_answer(selected_option):
    st.session_state.answered = True
    if selected_option == correct_meaning:
        st.session_state.streak += 1
        st.session_state.score += 10
        st.session_state.last_result = ("correct", selected_option)
        
        # Cập nhật điểm đúng vào file cá nhân
        if isinstance(data[target_word], dict):
            data[target_word]["correct"] = data[target_word].get("correct", 0) + 1
            save_data(data, data_file)
            
        if st.session_state.streak % 5 == 0:
            st.balloons()
    else:
        st.session_state.streak = 0
        st.session_state.last_result = ("wrong", selected_option)
        
        # Cập nhật điểm sai vào file cá nhân
        if isinstance(data[target_word], dict):
            data[target_word]["wrong"] = data[target_word].get("wrong", 0) + 1
            save_data(data, data_file)

if not st.session_state.get("answered", False):
    for idx, opt in enumerate(st.session_state.options):
        with grid_cols[idx]:
            if st.button(f"**{opt}**", key=f"btn_opt_{idx}", use_container_width=True):
                check_answer(opt)
                st.rerun()
else:
    res_type, selected_opt = st.session_state.last_result
    if res_type == "correct":
        st.success(f"🎉 **Chính xác!** `{target_word}` có nghĩa là **{correct_meaning}** (+10 điểm)")
    else:
        st.error(f"❌ **Tiếc quá!** Bạn chọn: *{selected_opt}*. Đáp án đúng là: **{correct_meaning}**")
        
    st.write("---")
    if st.button("🚀 Câu tiếp theo", type="primary", use_container_width=True):
        st.session_state.quiz_word = random.choice(all_words)
        st.session_state.answered = False
        st.rerun()
