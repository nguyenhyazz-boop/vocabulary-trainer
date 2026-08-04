import streamlit as st
from utils.data_manager import load_data, save_data

# 1. CẤU HÌNH TRANG VÀ GIAO DIỆN
st.set_page_config(page_title="Review Wrong Words", page_icon="❌", layout="centered")

# Thêm CSS để trang trí thẻ từ vựng cho đẹp mắt giống bản gốc
st.markdown("""
    <style>
    .word-card {
        background-color: #f1f2f6;
        border-radius: 15px;
        padding: 25px;
        box-shadow: 3px 3px 10px rgba(0,0,0,0.05);
        text-align: center;
        margin-bottom: 20px;
    }
    .word-title { color: #e84118; font-size: 40px; font-weight: bold; margin-bottom: 5px; }
    .word-pronounce { color: #7f8fa6; font-size: 18px; margin-bottom: 10px; }
    .word-type { color: #00a8ff; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("❌ Ôn Tập Từ Đã Sai")
st.write("Luyện tập lại những từ bạn chưa nhớ để ghi sâu vào não bộ!")
st.markdown("---")

# 2. TẢI DỮ LIỆU TỪ JSON
data = load_data()
words = data.get("words", [])

# Lọc danh sách các từ bị sai (count_wrong > 0)
wrong_words = [w for w in words if w.get("count_wrong", 0) > 0]

# Khởi tạo session_state để lưu vị trí từ đang ôn
if "wrong_index" not in st.session_state:
    st.session_state.wrong_index = 0

# ==========================================
# TRƯỜNG HỢP 1: KHI ĐÃ HỌC THUỘC HẾT TỪ SAI
# ==========================================
if not wrong_words:
    st.success("🎉 Xuất sắc! Bạn không còn từ nào làm sai nữa!")
    st.balloons()
    
    st.info("💡 Bạn có thể quay lại trang chủ để học từ mới, hoặc reset lại các từ sai để ôn tập lại từ đầu.")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # TÍNH NĂNG MỚI: Reset lại các từ sai để học lại
        if st.button("🔄 Luyện tập lại từ đầu", use_container_width=True):
            # Tìm những từ đã từng bị sai (count_wrong + count_correct > 0) để đưa vào danh sách học lại
            for w in words:
                if w.get("count_correct", 0) > 0 or w.get("count_wrong", 0) > 0:
                    w["count_wrong"] = 1 
            save_data(data)
            st.session_state.wrong_index = 0
            st.rerun()
            
    with col_b:
        # TÍNH NĂNG MỚI: Nút quay lại trang chủ an toàn
        if st.button("🏠 Về trang chủ (Study)", use_container_width=True):
            st.switch_page("app.py") # Lưu ý: Đảm bảo file chính của bạn tên là app.py hoặc 1_Study.py

# ==========================================
# TRƯỜNG HỢP 2: KHI VẪN CÒN TỪ SAI CẦN HỌC
# ==========================================
else:
    # Đảm bảo index không bị vượt quá số lượng từ
    if st.session_state.wrong_index >= len(wrong_words):
        st.session_state.wrong_index = 0

    total_wrong = len(wrong_words)
    current_idx = st.session_state.wrong_index
    current_word = wrong_words[current_idx]
    
    # FIX LỖI SẬP WEB: Đảm bảo progress luôn an toàn [0.0 -> 1.0]
    progress_val = (current_idx + 1) / total_wrong
    safe_progress = max(0.0, min(1.0, float(progress_val)))
    
    st.progress(safe_progress)
    st.caption(f"Tiến độ ôn tập: Từ **{current_idx + 1}** / {total_wrong}")

    # 3. HIỂN THỊ THẺ TỪ VỰNG (CARD)
    st.markdown(f"""
        <div class="word-card">
            <div class="word-title">{current_word.get('word', 'N/A')}</div>
            <div class="word-pronounce">{current_word.get('pronunciation', '')}</div>
            <div class="word-type">[{current_word.get('type', 'Từ vựng')}]</div>
        </div>
    """, unsafe_allow_html=True)

    # 4. HIỂN THỊ NGHĨA VÀ VÍ DỤ (Dạng mở rộng)
    with st.expander("👁️ Bấm vào đây để xem Nghĩa và Ví dụ", expanded=False):
        st.write(f"**📖 Ý nghĩa:** {current_word.get('meaning', 'Chưa có dữ liệu')}")
        if current_word.get('example'):
            st.info(f"**📝 Ví dụ:** *{current_word.get('example')}*")

    st.write("---")
    
    # 5. CÁC NÚT CHỨC NĂNG (Ghi nhận đúng/sai)
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Đã thuộc từ này!", type="primary", use_container_width=True):
            # Xóa lỗi sai, cộng điểm đúng
            for w in words:
                if w['word'] == current_word['word']:
                    w['count_wrong'] = 0 
                    w['count_correct'] = w.get('count_correct', 0) + 1
                    break
            save_data(data)
            # Cố định index, vì từ hiện tại bị xóa thì từ kế tiếp sẽ tự đẩy lên vị trí này
            st.rerun()

    with col2:
        if st.button("➡️ Bỏ qua (Chưa thuộc)", use_container_width=True):
            # Giữ nguyên lỗi sai, chuyển sang từ tiếp theo
            st.session_state.wrong_index = (st.session_state.wrong_index + 1) % len(wrong_words)
            st.rerun()

    # Nút phụ để quay lại hoặc làm mới
    st.write("")
    if st.button("🏠 Thoát về Trang chủ", use_container_width=True):
        st.switch_page("app.py")
