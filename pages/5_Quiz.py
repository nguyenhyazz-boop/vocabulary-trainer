import random
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Quiz - Vocabulary Trainer", page_icon="🧪", layout="wide")

st.title("🧪 Vocabulary Quiz")
st.caption("Thử thách kiểm tra trí nhớ từ vựng cá nhân của bạn!")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

if "quiz_mode" not in st.session_state:
    st.session_state.quiz_mode = "collocation"

# --- 1. CHỌN KHO TỪ VỰNG LÀM QUIZ ---
st.write("📌 **Chọn kho từ vựng bạn muốn kiểm tra:**")
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
    mode_title = "🔤 Normal Vocabulary"
else:
    data_file = f"data_collocation_{username}.json"
    mode_title = "🔗 Collocations & Phrases"

data = load_data(data_file)
all_words = list(data.keys())

if not all_words:
    st.info(f"Kho **{mode_title}** của bạn hiện chưa có từ vựng nào! Hãy sang **Library** để thêm từ trước nhé.")
    st.stop()

# --- 3. QUẢN LÝ CÂU HỎI QUIZ ---
if "quiz_word" not in st.session_state or st.session_state.quiz_word not in all_words:
    st.session_state.quiz_word = random.choice(all_words)

target_word = st.session_state.quiz_word
word_info = data[target_word]

if isinstance(word_info, dict):
    correct_meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    pos_tag = word_info.get("pos", "")
else:
    correct_meaning = str(word_info)
    pos_tag = ""

# --- 4. TẠO 4 LỰA CHỌN TRẮC NGHIỆM ---
if "options" not in st.session_state or st.session_state.get("current_target") != target_word:
    # Lấy các nghĩa sai từ từ vựng khác
    other_meanings = []
    for w, item in data.items():
        if w != target_word:
            m = item.get("meaning", str(item)) if isinstance(item, dict) else str(item)
            if m not in other_meanings:
                other_meanings.append(m)
    
    # Nếu không đủ từ trong kho để làm 4 lựa chọn, lấy thêm nghĩa mẫu
    default_fakes = ["nghiên cứu kỹ lưỡng", "tạo ra sự khác biệt", "chuẩn bị hành lý", "giữ liên lạc", "thực hiện kế hoạch"]
    for f in default_fakes:
        if len(other_meanings) < 3 and f != correct_meaning:
            other_meanings.append(f)

    selected_fakes = random.sample(other_meanings, min(3, len(other_meanings)))
    opts = selected_fakes + [correct_meaning]
    random.shuffle(opts)
    
    st.session_state.options = opts
    st.session_state.current_target = target_word

# --- 5. HIỂN THỊ CÂU HỎI ---
pos_display = f" (*{pos_tag}*)" if pos_tag else ""
st.subheader(f"Từ vựng: **{target_word}**{pos_display}")
st.write("Chọn nghĩa đúng nhất của từ/cụm từ trên:")

user_choice = st.radio("Các phương án:", st.session_state.options, key=f"radio_{target_word}")

if st.button("🎯 Kiểm tra đáp án", type="primary", use_container_width=True):
    if user_choice == correct_meaning:
        st.success("🎉 Chính xác! Bạn nhớ từ rất tốt.")
        
        # Cập nhật điểm đúng
        if isinstance(data[target_word], dict):
            data[target_word]["correct"] = data[target_word].get("correct", 0) + 1
            save_data(data, data_file)
    else:
        st.error(f"❌ Sai rồi! Đáp án đúng là: **{correct_meaning}**")
        
        # Cập nhật điểm sai
        if isinstance(data[target_word], dict):
            data[target_word]["wrong"] = data[target_word].get("wrong", 0) + 1
            save_data(data, data_file)

st.write("---")
if st.button("➡️ Câu tiếp theo", use_container_width=True):
    st.session_state.quiz_word = random.choice(all_words)
    st.rerun()
