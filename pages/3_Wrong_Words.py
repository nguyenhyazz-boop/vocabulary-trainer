import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Review Wrong Words", page_icon="❌")
st.title("❌ Ôn Tập Từ Sai")

data = load_data()
words = data.get("words", [])

wrong_words = [w for w in words if w.get("count_wrong", 0) > 0]

if "wrong_index" not in st.session_state:
    st.session_state.wrong_index = 0

if not wrong_words:
    st.warning("📭 Hiện tại không có từ nào bị sai cả!")
    st.info("💡 Bạn có thể bấm nút bên dưới để ép toàn bộ từ vựng ra ôn tập lại:")
    
    # Đã thêm st.rerun() ở đây để bấm phát là ăn ngay lập tức
    if st.button("⚡ Bấm vào đây để hiện lại toàn bộ từ vựng", use_container_width=True):
        for w in words:
            w["count_wrong"] = 1
        save_data(data)
        st.session_state.wrong_index = 0
        st.rerun()
else:
    if st.session_state.wrong_index >= len(wrong_words):
        st.session_state.wrong_index = 0

    total = len(wrong_words)
    idx = st.session_state.wrong_index
    curr = wrong_words[idx]

    st.progress(min(1.0, max(0.0, (idx + 1) / total)))
    st.write(f"Đang ôn từ: **{idx + 1}** / {total}")

    st.subheader(curr.get('word', ''))
    st.write(f"**Loại từ:** {curr.get('type', '')} | **Phiên âm:** {curr.get('pronunciation', '')}")
    
    with st.expander("Xem nghĩa"):
        st.write(curr.get('meaning', ''))
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
            st.rerun()
    with col2:
        if st.button("➡️ Bỏ qua", use_container_width=True):
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()
