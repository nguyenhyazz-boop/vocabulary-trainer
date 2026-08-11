import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library - Vocabulary Trainer", page_icon="📚", layout="wide")

st.title("📚 Ngân hàng từ vựng mẫu")
st.caption("Chọn những từ bạn chưa biết theo chủ đề để thêm vào bộ sưu tập cá nhân!")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Đọc kho mẫu và kho cá nhân của user
sample_data = load_data("sample_words.json")
user_colloc = load_data(f"data_collocation_{username}.json")
user_vocab = load_data(f"data_vocab_{username}.json")

user_all_words = {**user_colloc, **user_vocab}

if not sample_data:
    st.info("Chưa có từ vựng mẫu nào trong hệ thống.")
    st.stop()

# --- 1. BỘ LỌC THEO CHỦ ĐỀ ---
topics = list(set(item.get("topic", "Khác") for item in sample_data.values() if isinstance(item, dict)))
selected_topic = st.selectbox("🎯 Chọn chủ đề bạn muốn xem:", ["Tất cả chủ đề"] + topics)

# Ô tìm kiếm từ vựng
search_query = st.text_input("🔎 Tìm từ cụ thể:", "").strip().lower()

# Lọc danh sách từ
filtered_words = {}
for word, item in sample_data.items():
    if isinstance(item, dict):
        match_topic = (selected_topic == "Tất cả chủ đề") or (item.get("topic") == selected_topic)
        match_search = (search_query in word.lower()) or (search_query in item.get("meaning", "").lower())
        if match_topic and match_search:
            filtered_words[word] = item

st.write(f"Tìm thấy **{len(filtered_words)}** từ vựng mẫu:")
st.divider()

# --- 2. HIỂN THỊ DANH SÁCH & NÚT THÊM ---
for word, item in filtered_words.items():
    meaning = item.get("meaning", "")
    w_type = item.get("type", "vocab")
    w_topic = item.get("topic", "Chung")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        type_badge = "🔗 Collocation" if w_type == "collocation" else "🔤 Vocab"
        st.markdown(f"📌 **{word}** (`{type_badge}` | 🏷️ *{w_topic}*) — **{meaning}**")
        
    with col2:
        if word in user_all_words:
            st.success("✅ Đã có trong bộ học")
        else:
            if st.button("➕ Thêm vào bộ học", key=f"add_{word}", type="primary"):
                target_file = f"data_collocation_{username}.json" if w_type == "collocation" else f"data_vocab_{username}.json"
                user_repo = load_data(target_file)
                
                user_repo[word] = {
                    "meaning": meaning,
                    "topic": w_topic,
                    "correct": 0,
                    "wrong": 0
                }
                save_data(user_repo, target_file)
                st.success(f"Đã thêm **{word}**!")
                st.rerun()
