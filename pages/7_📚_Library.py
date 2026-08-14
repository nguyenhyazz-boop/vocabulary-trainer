import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library", page_icon="📚", layout="wide")

st.title("📚 Thư viện từ vựng có sẵn")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Đọc file dữ liệu gốc (kho 800 từ dùng chung hoặc file cá nhân)
vocab_file = f"data_vocab_{username}.json"
colloc_file = f"data_collocation_{username}.json"

# Nếu không tìm thấy file user, sẽ tự đọc file mặc định gốc (data_vocab.json / data_collocation.json)
vocab_data = load_data(vocab_file)
if not vocab_data:
    vocab_data = load_data("data_vocab.json")

colloc_data = load_data(colloc_file)
if not colloc_data:
    colloc_data = load_data("data_collocation.json")

if not isinstance(vocab_data, dict): vocab_data = {}
if not isinstance(colloc_data, dict): colloc_data = {}

tab1, tab2 = st.tabs(["Từ vựng thông thường (Vocab)", "Cụm từ (Collocations)"])

with tab1:
    st.subheader(f"Danh sách từ vựng ({len(vocab_data)} từ)")
    search_v = st.text_input("🔍 Tìm kiếm từ vựng trong kho:", key="search_v_lib").strip().lower()
    
    filtered_v = {k: v for k, v in vocab_data.items() if search_v in k.lower() or search_v in v.get("meaning", "").lower()}
    
    if not filtered_v:
        st.info("Không tìm thấy từ vựng nào.")
    else:
        for word, info in filtered_v.items():
            with st.expander(f"📌 **{word}** — {info.get('meaning', '')}"):
                if "pos" in info:
                    st.write(f"**Loại từ:** {info['pos']}")
                if "example" in info and info["example"]:
                    st.write(f"**Ví dụ:** *{info['example']}*")
                
                col_del, _ = st.columns([1, 4])
                with col_del:
                    if st.button("Xóa khỏi kho", key=f"del_lib_v_{word}"):
                        del vocab_data[word]
                        save_data(vocab_data, vocab_file)
                        st.rerun()

with tab2:
    st.subheader(f"Danh sách cụm từ ({len(colloc_data)} cụm từ)")
    search_c = st.text_input("🔍 Tìm kiếm cụm từ trong kho:", key="search_c_lib").strip().lower()
    
    filtered_c = {k: v for k, v in colloc_data.items() if search_c in k.lower() or search_c in v.get("meaning", "").lower()}
    
    if not filtered_c:
        st.info("Không tìm thấy cụm từ nào.")
    else:
        for word, info in filtered_c.items():
            with st.expander(f"📌 **{word}** — {info.get('meaning', '')}"):
                if "example" in info and info["example"]:
                    st.write(f"**Ví dụ:** *{info['example']}*")
                
                col_del, _ = st.columns([1, 4])
                with col_del:
                    if st.button("Xóa khỏi kho", key=f"del_lib_c_{word}"):
                        del colloc_data[word]
                        save_data(colloc_data, colloc_file)
                        st.rerun()
