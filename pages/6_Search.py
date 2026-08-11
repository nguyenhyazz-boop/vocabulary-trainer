import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Search & Edit - Vocabulary Trainer", page_icon="🔍", layout="wide")

st.title("🔍 Tìm kiếm & Quản lý từ vựng cá nhân")
st.caption("Tra cứu từ vựng cá nhân, chỉnh sửa nghĩa hoặc xóa từ không cần thiết.")

# Kiểm tra trạng thái đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

colloc_file = f"data_collocation_{username}.json"
vocab_file = f"data_vocab_{username}.json"

colloc_data = load_data(colloc_file)
vocab_data = load_data(vocab_file)

# Gộp bộ từ vựng cá nhân của người dùng
user_data = {**colloc_data, **vocab_data}

if not user_data:
    st.info("Bộ từ vựng cá nhân của bạn hiện đang trống. Hãy thêm từ mới hoặc chọn từ trong Library!")
    st.stop()

# --- Ô TÌM KIẾM THỜI GIAN THỰC ---
search_query = st.text_input("🔎 Nhập từ vựng hoặc nghĩa cần tìm:", "").strip().lower()

if search_query:
    filtered_words = {
        w: item for w, item in user_data.items()
        if search_query in w.lower() or (isinstance(item, dict) and search_query in item.get("meaning", "").lower())
    }
else:
    filtered_words = user_data

st.write(f"Tìm thấy **{len(filtered_words)}** từ trong bộ sưu tập của bạn:")
st.divider()

# --- HIỂN THỊ DANH SÁCH TÌM KIẾM VÀ CHỨC NĂNG SỬA/XÓA ---
for word, item in filtered_words.items():
    meaning = item.get("meaning", "") if isinstance(item, dict) else str(item)
    w_type = "collocation" if word in colloc_data else "vocab"
    target_file = colloc_file if w_type == "collocation" else vocab_file
    
    with st.expander(f"📌 **{word}** — *{meaning}*"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_meaning = st.text_input("Chỉnh sửa nghĩa:", value=meaning, key=f"edit_{word}")
            if st.button("💾 Cập nhật", key=f"btn_save_{word}"):
                repo = load_data(target_file)
                if word in repo:
                    if isinstance(repo[word], dict):
                        repo[word]["meaning"] = new_meaning.strip()
                    else:
                        repo[word] = {"meaning": new_meaning.strip(), "correct": 0, "wrong": 0}
                    save_data(repo, target_file)
                    st.success(f"Đã cập nhật nghĩa cho **{word}**!")
                    st.rerun()
                
        with col2:
            st.write("---")
            if st.button("🗑️ Xóa từ này", key=f"btn_del_{word}", type="primary"):
                repo = load_data(target_file)
                if word in repo:
                    del repo[word]
                    save_data(repo, target_file)
                    st.warning(f"Đã xóa **{word}** khỏi danh sách!")
                    st.rerun()
