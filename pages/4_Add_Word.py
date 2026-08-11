import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Add Word - Vocabulary Trainer", page_icon="➕", layout="wide")

st.title("➕ Thêm từ vựng mới")
st.caption("Thêm từ mới vào kho dữ liệu tương ứng.")

with st.form("add_word_form", clear_on_submit=True):
    word = st.text_input("Từ vựng / Collocation (tiếng Anh):").strip().lower()
    meaning = st.text_input("Nghĩa (tiếng Việt):").strip()
    
    target_repo = st.radio(
        "📂 Chọn kho lưu trữ:",
        ["🔤 Normal Vocabulary (`data_vocab.json`)", "🔗 Collocations (`data_collocation.json`)"],
        horizontal=True
    )
    
    submitted = st.form_submit_button("💾 Lưu vào kho", use_container_width=True)

if submitted:
    target_file = "data_collocation.json" if "Collocations" in target_repo else "data_vocab.json"
    data = load_data(target_file)
    
    if not word or not meaning:
        st.error("⚠️ Vui lòng nhập đầy đủ cả từ vựng và nghĩa!")
    elif word in data:
        st.warning(f"⚠️ Từ **'{word}'** đã tồn tại trong kho `{target_file}`!")
    else:
        data[word] = {
            "meaning": meaning,
            "correct": 0,
            "wrong": 0
        }
        save_data(data, target_file)
        st.success(f"🎉 Đã thêm **'{word}'** vào kho `{target_file}` thành công!")
