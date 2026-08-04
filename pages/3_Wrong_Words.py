import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Review Wrong Words", page_icon="❌")
st.title("❌ Ôn Tập Từ Sai")

# 1. Tải dữ liệu
data = load_data()
words = data.get("words", [])

# 2. Lọc danh sách từ có count_wrong > 0
wrong_words = [w for w in words if w.get("count_wrong", 0) > 0]

# 3. Quản lý index an toàn
if "wrong_index" not in st.session_state:
    st.session_state.wrong_index = 0

# Nếu danh sách sai trống
if not wrong_words:
    st.warning("📭 Hiện tại danh sách từ sai đang trống.")
    
    # Nút ép reset index và nạp lại toàn bộ từ sai
    if st.button("🔄 Nạp lại danh sách từ sai", use_container_width=True):
        for w in words:
            w["count_wrong"] = 1
        save_data(data)
        # Xóa sạch session cũ để ép làm mới hoàn toàn
        if "wrong_index" in st.session_state:
            del st.session_state.wrong_index
        st.rerun()
else:
    # Đảm bảo index không bị trôi ra ngoài độ dài mảng
    if st.session_state.wrong_index >= len(wrong_words):
        st.session_state.wrong_index = 0

    total = len(wrong_words)
    idx = st.session_state.wrong_index
    curr = wrong_words[idx]

    # Thanh tiến trình
    st.progress(min(1.0, max(0.0, (idx + 1) / total)))
    st.write(f"Đang ôn từ: **{idx + 1}** / {total}")

    # Hiển thị thông tin từ vựng
    st.subheader(curr.get('word', ''))
    st.write(f"**Loại từ:** {curr.get('type', 'N/A')} | **Phiên âm:** {curr.get('pronunciation', 'N/A')}")
    
    with st.expander("Xem nghĩa"):
        st.write(curr.get('meaning', 'N/A'))
        if curr.get('example'):
            st.write(f"Ví dụ: {curr.get('example')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Đã nhớ", use_container_width=True):
            for w in words:
                if w['word'] == curr['word']:
                    w['count_wrong'] = 0
                    w['count_correct'] = w.get('count_correct', 0) + 1
                    break
            save_data(data)
            # Reset lại index về 0 để không bị lệch mảng khi bớt từ đi
            st.session_state.wrong_index = 0
            st.rerun()
            
    with col2:
        if st.button("➡️ Bỏ qua", use_container_width=True):
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()
