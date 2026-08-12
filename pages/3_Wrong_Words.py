import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Wrong Words - Vocabulary Trainer", page_icon="❌", layout="wide")

st.title("❌ Wrong Words List")
st.caption("Danh sách các từ vựng bạn đã trả lời sai. Hãy ôn tập lại để ghi nhớ tốt hơn!")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# --- 1. ĐỌC DỮ LIỆU CÁ NHÂN CỦA USER ---
colloc_file = f"data_collocation_{username}.json"
vocab_file = f"data_vocab_{username}.json"

colloc_data = load_data(colloc_file)
vocab_data = load_data(vocab_file)

# Gộp toàn bộ từ vựng cá nhân
user_all_words = {}
for w, item in colloc_data.items():
    if isinstance(item, dict):
        item["file_type"] = colloc_file
        user_all_words[w] = item

for w, item in vocab_data.items():
    if isinstance(item, dict):
        item["file_type"] = vocab_file
        user_all_words[w] = item

# --- 2. LỌC CÁC TỪ CÓ ĐIỂM SAI (WRONG > 0) ---
wrong_list = {
    w: item for w, item in user_all_words.items()
    if isinstance(item, dict) and item.get("wrong", 0) > 0
}

if not wrong_list:
    st.balloons()
    st.success("🎉 Tuyệt vời! Hiện tại bạn không có từ nào bị đánh dấu sai cả.")
    st.stop()

st.write(f"📌 Bạn có **{len(wrong_list)}** từ cần ôn tập lại:")
st.divider()

# --- 3. HIỂN THỊ DANH SÁCH TỪ SAI VÀ NÚT ĐÁNH DẤU ĐÃ THUỘC ---
for word, item in wrong_list.items():
    meaning = item.get("meaning", "")
    pos_tag = item.get("pos", "")
    wrong_cnt = item.get("wrong", 0)
    correct_cnt = item.get("correct", 0)
    target_file = item.get("file_type")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        pos_display = f" (*{pos_tag}*)" if pos_tag else ""
        st.markdown(f"🔴 **{word}**{pos_display} — **{meaning}**")
        st.caption(f"📊 Kết quả: Sai **{wrong_cnt}** lần | Đúng **{correct_cnt}** lần")
        
    with col2:
        # Nút xóa khỏi danh sách sai (Reset số lần sai về 0)
        if st.button("✅ Đã thuộc từ này", key=f"fixed_{word}", use_container_width=True):
            file_data = load_data(target_file)
            if word in file_data and isinstance(file_data[word], dict):
                file_data[word]["wrong"] = 0
                save_data(file_data, target_file)
                st.success(f"Đã gạch tên **{word}** khỏi danh sách sai!")
                st.rerun()
    st.write("---")
with col2:
    if st.button("❌ Wrong", use_container_width=True):
        handle_wrong_answer(False)
        st.rerun()
