import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Review Wrong Words", page_icon="❌")
st.title("❌ Review Wrong Words")

# Tải dữ liệu
data = load_data()
words = data.get("words", [])

# Lọc danh sách các từ bị sai
wrong_words = [w for w in words if w.get("count_wrong", 0) > 0]

# Khởi tạo vị trí từ đang ôn
if "wrong_index" not in st.session_state:
    st.session_state.wrong_index = 0

# NẾU ĐÃ THUỘC HẾT TỪ SAI (Danh sách trống)
if not wrong_words:
    st.success("🎉 Bạn đã hoàn thành xuất sắc tất cả các từ sai!")
    st.balloons()
    
    st.write("---")
    st.write("💡 Hãy dùng Menu bên trái để chuyển sang trang **Quiz Mode** hoặc **Study** nhé!")
    
    # Nút thử nghiệm: Ép tất cả từ vựng thành "Từ sai" để có dữ liệu test lại trang này
    if st.button("🔄 Thử nghiệm: Thêm lại tất cả từ vựng vào mục từ sai", use_container_width=True):
        for w in words:
            w["count_wrong"] = 1
        save_data(data)
        st.session_state.wrong_index = 0
        st.rerun()

# NẾU CÒN TỪ SAI (Hiển thị giao diện ôn tập)
else:
    # Đảm bảo index không bị quá độ dài danh sách
    if st.session_state.wrong_index >= len(wrong_words):
        st.session_state.wrong_index = 0

    total_wrong = len(wrong_words)
    current_idx = st.session_state.wrong_index
    
    # CÔNG THỨC SỬA LỖI PROGRESS (Ví dụ: Từ 1/5 -> Tiến trình 0.2)
    progress_val = (current_idx + 1) / total_wrong
    st.progress(progress_val)
    st.caption(f"Đang ôn từ {current_idx + 1} / {total_wrong}")

    current_word = wrong_words[current_idx]

    # Hiển thị từ vựng
    st.subheader(f"Từ: **{current_word.get('word', '')}**")
    st.write(f"**Loại từ:** {current_word.get('type', 'N/A')}")
    st.write(f"**Phiên âm:** {current_word.get('pronunciation', 'N/A')}")

    with st.expander("Xem nghĩa của từ"):
        st.write(f"**Nghĩa:** {current_word.get('meaning', '')}")
        if current_word.get('example'):
            st.write(f"**Ví dụ:** {current_word.get('example', '')}")

    st.write("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Đã nhớ", use_container_width=True):
            # Xóa lỗi của từ này trong database
            for w in words:
                if w['word'] == current_word['word']:
                    w['count_wrong'] = 0 
                    break
            save_data(data)
            st.rerun() # Refresh lại trang để mất từ vừa bấm

    with col2:
        if st.button("➡️ Bỏ qua (Xem từ kế tiếp)", use_container_width=True):
            # Chuyển sang từ tiếp theo
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()
