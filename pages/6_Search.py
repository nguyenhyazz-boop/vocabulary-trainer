import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Search & Edit - Vocabulary Trainer", page_icon="🔍", layout="wide")

st.title("🔍 Tìm kiếm & Quản lý từ vựng")
st.caption("Tra cứu, chỉnh sửa nghĩa hoặc xóa từ vựng trong hệ thống.")

data = load_data()

if not data:
    st.info("Chưa có từ vựng nào trong dữ liệu.")
    st.stop()

# Thanh tìm kiếm
search_query = st.text_input("🔎 Nhập từ vựng hoặc nghĩa cần tìm:", "").strip().lower()

# Lọc danh sách từ
filtered_words = {
    w: m for w, m in data.items() 
    if search_query in w.lower() or search_query in m.get("meaning", "").lower()
}

st.write(f"Tìm thấy **{len(filtered_words)}** từ vựng:")

st.divider()

# Hiển thị kết quả dưới dạng thẻ (Expander)
for word, item in filtered_words.items():
    with st.expander(f"📌 **{word}** — *{item.get('meaning', '')}*"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_meaning = st.text_input("Chỉnh sửa nghĩa:", value=item.get("meaning", ""), key=f"edit_{word}")
            if st.button("💾 Cập nhật", key=f"btn_save_{word}"):
                data[word]["meaning"] = new_meaning.strip()
                save_data(data)
                st.success(f"Đã cập nhật nghĩa cho từ **{word}**!")
                st.rerun()
                
        with col2:
            st.write("---")
            if st.button("🗑️ Xóa từ này", key=f"btn_del_{word}", type="primary"):
                del data[word]
                save_data(data)
                st.warning(f"Đã xóa từ **{word}** khỏi danh sách!")
                st.rerun()
