import streamlit as st
from utils.data_manager import load_data, save_data

# Cấu hình trang
st.set_page_config(page_title="Review Wrong Words", page_icon="❌")

st.title("❌ Review Wrong Words")

# Load dữ liệu
data = load_data()
words = data.get("words", [])

# Lọc danh sách các từ bị sai (count_wrong > 0)
wrong_words = [w for w in words if w.get("count_wrong", 0) > 0]

# Khởi tạo chỉ số từ hiện tại trong session_state
if "wrong_index" not in st.session_state:
    st.session_state.wrong_index = 0

# KIỂM TRA: Nếu không có từ sai nào (hoặc đã ôn xong hết)
if not wrong_words:
    st.success("🎉 Bạn đã hoàn thành xuất sắc tất cả các từ sai!")
    st.balloons()
    st.info("💡 Hãy sang mục Quiz làm bài luyện tập. Nếu làm sai câu nào, từ đó sẽ tự động xuất hiện lại ở đây nhé!")
        st.session_state.wrong_index = 0
        st.rerun()
else:
    # Đảm bảo index không vượt quá độ dài danh sách
    if st.session_state.wrong_index >= len(wrong_words):
        st.session_state.wrong_index = 0

    # TÍNH TIẾN TRÌNH AN TOÀN (Tránh lỗi Progress Value invalid)
    total_wrong = len(wrong_words)
    current_idx = st.session_state.wrong_index
    progress_val = float(current_idx) / float(total_wrong)
    progress_val = max(0.0, min(1.0, progress_val)) # Giới hạn chuẩn [0.0, 1.0]
    
    st.progress(progress_val)
    st.caption(f"Đang ôn từ {current_idx + 1} / {total_wrong}")

    current_word = wrong_words[st.session_state.wrong_index]

    # Hiển thị từ vựng
    st.subheader(f"Từ: **{current_word['word']}**")
    st.write(f"**Loại từ:** {current_word.get('type', 'N/A')}")
    st.write(f"**Phiên âm:** {current_word.get('pronunciation', 'N/A')}")

    # Nút bấm hiện nghĩa
    with st.expander("Xem nghĩa của từ"):
        st.write(f"**Nghĩa:** {current_word['meaning']}")
        if current_word.get('example'):
            st.write(f"**Ví dụ:** {current_word['example']}")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Đã nhớ (Đánh dấu đúng)", use_container_width=True):
            # Giảm số lần sai hoặc trừ về 0 khi đã thuộc
            for w in words:
                if w['word'] == current_word['word']:
                    w['count_wrong'] = max(0, w.get('count_wrong', 0) - 1)
                    w['count_correct'] = w.get('count_correct', 0) + 1
                    break
            save_data(data)
            st.success("Đã ghi nhận!")
            st.rerun()

    with col2:
        if st.button("➡️ Bỏ qua / Từ tiếp theo", use_container_width=True):
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()
