import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Review Wrong Words", page_icon="❌")

st.title("❌ Ôn Tập Từ Sai")

# Load dữ liệu
data = load_data()
words = data.get("words", [])

# Lọc các từ sai (count_wrong > 0)
wrong_words = [w for w in words if w.get("count_wrong", 0) > 0]

if "wrong_index" not in st.session_state:
    st.session_state.wrong_index = 0

# TRƯỜNG HỢP: Đã thuộc hết từ sai
if not wrong_words:
    st.success("🎉 Bạn đã thuộc hết các từ từng làm sai!")
    st.balloons()
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔄 Reset lại tất cả từ sai để học lại", use_container_width=True):
            # Khôi phục lại đếm sai cho các từ để học lại
            for w in words:
                if w.get("count_correct", 0) > 0:
                    w["count_wrong"] = 1
            save_data(data)
            st.session_state.wrong_index = 0
            st.rerun()
            
    with col_b:
        if st.button("🏠 Về trang chính (App)", use_container_width=True):
            st.switch_page("app.py")

# TRƯỜNG HỢP: Còn từ sai cần ôn
else:
    if st.session_state.wrong_index >= len(wrong_words):
        st.session_state.wrong_index = 0

    total_wrong = len(wrong_words)
    current_idx = st.session_state.wrong_index
    
    # Tiến trình an toàn [0.0 -> 1.0]
    progress_val = float(current_idx) / float(total_wrong)
    progress_val = max(0.0, min(1.0, progress_val))
    
    st.progress(progress_val)
    st.caption(f"Đang ôn từ {current_idx + 1} / {total_wrong} từ sai")

    current_word = wrong_words[st.session_state.wrong_index]

    # Màn hình hiển thị từ
    st.subheader(f"Từ vựng: **{current_word['word']}**")
    st.write(f"**Loại từ:** {current_word.get('type', 'N/A')}")
    st.write(f"**Phiên âm:** {current_word.get('pronunciation', 'N/A')}")

    with st.expander("👁️ Bấm để xem nghĩa"):
        st.write(f"**Nghĩa:** {current_word['meaning']}")
        if current_word.get('example'):
            st.write(f"**Ví dụ:** {current_word['example']}")

    st.write("---")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        if st.button("✅ Đã thuộc", use_container_width=True):
            for w in words:
                if w['word'] == current_word['word']:
                    w['count_wrong'] = max(0, w.get('count_wrong', 0) - 1)
                    w['count_correct'] = w.get('count_correct', 0) + 1
                    break
            save_data(data)
            st.rerun()

    with c2:
        if st.button("➡️ Bỏ qua", use_container_width=True):
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()
            
    with c3:
        if st.button("🏠 Trang chủ", use_container_width=True):
            st.switch_page("app.py")

    with col2:
        if st.button("➡️ Bỏ qua / Từ tiếp theo", use_container_width=True):
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()
