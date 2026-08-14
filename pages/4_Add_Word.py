import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Add New Word - Vocabulary Trainer", page_icon="➕", layout="wide")

st.title("➕ Thêm từ vựng mới")
st.caption("Thêm từ mới kèm loại từ (Danh từ, Động từ, Tính từ...) vào kho cá nhân!")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# 1. Chọn kho lưu trữ
category = st.radio("Kho lưu trữ:", ["Từ vựng thông thường (Vocab)", "Cụm từ cố định (Collocation)"], horizontal=True)

if category == "Cụm từ cố định (Collocation)":
    file_name = f"data_collocation_{username}.json"
else:
    file_name = f"data_vocab_{username}.json"

current_data = load_data(file_name)
if not isinstance(current_data, dict):
    current_data = {}

st.divider()

# 2. Form thêm từ
with st.form("add_word_form", clear_on_submit=True):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        new_word = st.text_input("Từ / Cụm từ Tiếng Anh:", placeholder="vd: hello, permanent, take action").strip()
    
    with col2:
        # THÊM MỤC CHỌN LOẠI TỪ TẠI ĐÂY!
        word_pos = st.selectbox(
            "Loại từ (Part of Speech):",
            [
                "Noun (n) - Danh từ",
                "Verb (v) - Động từ",
                "Adjective (adj) - Tính từ",
                "Adverb (adv) - Trạng từ",
                "Phrase / Idiom - Cụm từ / Thành ngữ",
                "Preposition (prep) - Giới từ",
                "Other - Khác"
            ]
        )

    new_meaning = st.text_input("Nghĩa Tiếng Việt:", placeholder="vd: xin chào, vĩnh viễn, hành động").strip()
    example_sentence = st.text_input("Ví dụ minh họa (không bắt buộc):", placeholder="vd: She said hello to everyone.").strip()

    submitted = st.form_submit_button("📌 Lưu Từ Vựng Ngay", type="primary", use_container_width=True)

    if submitted:
        if not new_word or not new_meaning:
            st.error("❌ Vui lòng nhập đầy đủ Từ tiếng Anh và Nghĩa tiếng Việt!")
        else:
            word_key = new_word.lower()
            
            # Lấy ký hiệu viết tắt loại từ (ví dụ: Noun, Verb, Adj...)
            pos_short = word_pos.split(" ")[0]

            # Lưu đầy đủ thông tin nâng cấp
            current_data[word_key] = {
                "meaning": new_meaning,
                "pos": pos_short,  # Loại từ
                "example": example_sentence, # Câu ví dụ
                "correct": current_data.get(word_key, {}).get("correct", 0),
                "wrong": current_data.get(word_key, {}).get("wrong", 0)
            }

            save_data(current_data, file_name)
            st.success(f"🎉 Đã thêm từ **'{new_word}'** (`{pos_short}`): *{new_meaning}* vào bộ sưu tập!")
            st.balloons()
