import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library - Vocabulary Trainer", page_icon="📚", layout="wide")

st.title("📚 Vocabulary Library")
st.caption("Khám phá từ vựng mẫu theo từng chủ đề và chọn từ chưa biết để thêm vào bộ sưu tập cá nhân.")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Đọc kho từ vựng mẫu và kho cá nhân của user
sample_data = load_data("sample_words.json")
user_colloc = load_data(f"data_collocation_{username}.json")
user_vocab = load_data(f"data_vocab_{username}.json")

user_all_words = {**user_colloc, **user_vocab}

if not sample_data:
    st.info("Chưa có từ vựng mẫu nào trong thư viện. Vui lòng kiểm tra lại file sample_words.json!")
    st.stop()

# --- 1. DANH SÁCH CÁC CHỦ ĐỀ (TOPICS) ---
topics = sorted(list(set(item.get("topic", "Khác") for item in sample_data.values() if isinstance(item, dict))))

st.subheader("🎯 Chọn chủ đề bạn muốn khám phá:")
selected_topic = st.radio("Chủ đề:", topics, horizontal=True)

st.divider()

# --- 2. LỌC VÀ HIỂN THỊ TỪ VỰNG THEO CHỦ ĐỀ ĐÃ CHỌN ---
topic_words = {
    w: item for w, item in sample_data.items()
    if isinstance(item, dict) and item.get("topic") == selected_topic
}

st.write(f"Chủ đề **{selected_topic}** có **{len(topic_words)}** từ vựng mẫu:")

for word, item in topic_words.items():
    meaning = item.get("meaning", "")
    w_type = item.get("type", "vocab")
    pos_tag = item.get("pos", "")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        type_badge = "🔗 Collocation" if w_type == "collocation" else "🔤 Vocab"
        pos_display = f" (*{pos_tag}*)" if pos_tag else ""
        st.markdown(f"📌 **{word}**{pos_display} (`{type_badge}`) — **{meaning}**")
        
    with col2:
        if word in user_all_words:
            st.success("✅ Đã có trong bộ học")
        else:
            if st.button("➕ Thêm vào bộ học", key=f"lib_add_{word}", type="primary"):
                target_file = f"data_collocation_{username}.json" if w_type == "collocation" else f"data_vocab_{username}.json"
                user_repo = load_data(target_file)
                
                user_repo[word] = {
                    "meaning": meaning,
                    "topic": selected_topic,
                    "pos": pos_tag,
                    "correct": 0,
                    "wrong": 0
                }
                save_data(user_repo, target_file)
                st.success(f"Đã thêm **{word}**!")
                st.rerun()
