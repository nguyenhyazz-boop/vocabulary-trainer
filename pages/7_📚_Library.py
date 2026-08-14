import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library", page_icon="📚", layout="wide")

st.title("📚 Thư viện từ vựng")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

vocab_file = f"data_vocab_{username}.json"
colloc_file = f"data_collocation_{username}.json"

vocab_data = load_data(vocab_file)
if not isinstance(vocab_data, dict):
    vocab_data = {}

colloc_data = load_data(colloc_file)
if not isinstance(colloc_data, dict):
    colloc_data = {}

tab1, tab2 = st.tabs(["Từ vựng (Vocab)", "Cụm từ (Collocations)"])

with tab1:
    st.subheader("Danh sách từ vựng")
    if not vocab_data:
        st.info("Chưa có từ vựng nào.")
    else:
        for word, info in list(vocab_data.items()):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.write(f"**{word}**")
            with col2:
                st.write(info.get("meaning", ""))
            with col3:
                if st.button("Xóa", key=f"del_v_{word}"):
                    del vocab_data[word]
                    save_data(vocab_data, vocab_file)
                    st.rerun()

with tab2:
    st.subheader("Danh sách cụm từ")
    if not colloc_data:
        st.info("Chưa có cụm từ nào.")
    else:
        for word, info in list(colloc_data.items()):
            col1, col2, col3 = st.columns([3, 3, 1])
            with col1:
                st.write(f"**{word}**")
            with col2:
                st.write(info.get("meaning", ""))
            with col3:
                if st.button("Xóa", key=f"del_c_{word}"):
                    del colloc_data[word]
                    save_data(colloc_data, colloc_file)
                    st.rerun()
