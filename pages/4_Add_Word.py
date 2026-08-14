import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Add New Word", page_icon="➕", layout="wide")

st.title("➕ Thêm từ vựng mới")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Chọn loại từ vựng
word_type = st.radio("Chọn loại từ vựng:", ["Từ đơn (Normal Vocab)", "Cụm từ (Collocation)"], horizontal=True)

if word_type == "Cụm từ (Collocation)":
    file_name = f"data_collocation_{username}.json"
else:
    file_name = f"data_vocab_{username}.json"

# Đọc dữ liệu hiện tại
current_data = load_data(file_name)
if not isinstance(current_data, dict):
    current_data = {}

with st.form("add_word_form", clear_on_submit=True):
    new_word = st.text_input("Nhập Từ/Cụm từ tiếng Anh:").strip()
    new_meaning = st.text_input("Nhập Nghĩa tiếng Việt:").strip()
    
    submitted = st.form_submit_button("📌 Lưu từ vựng", use_container_width=True)
    
    if submitted:
        if not new_word or not new_meaning:
            st.error("❌ Vui lòng nhập đầy đủ cả từ tiếng Anh và nghĩa tiếng Việt!")
        else:
            # Chuyển từ về chữ thường để tránh trùng lặp hoa/thường
            word_key = new_word.lower()
            
            # Lưu cấu trúc chuẩn
            current_data[word_key] = {
                "meaning": new_meaning,
                "correct": 0,
                "wrong": 0
            }
            
            # Ghi trực tiếp vào file JSON của User
            save_data(current_data, file_name)
            st.success(f"🎉 Đã thêm thành công từ **'{new_word}'** (`{new_meaning}`) vào bộ sưu tập!")
            st.balloons()
