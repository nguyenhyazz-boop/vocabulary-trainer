import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library | Vocabulary Trainer", page_icon="📚", layout="wide")

# --- CUSTOM CSS: GIAO DIỆN CHUẨN MODERN SAAS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Header */
    .app-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Card thiết kế từ vựng mẫu */
    .sample-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease-in-out;
    }
    .sample-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.06);
    }
    .sample-word {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
    }
    .sample-meaning {
        font-size: 1rem;
        color: #334155;
        font-weight: 500;
        margin-top: 6px;
    }

    /* Badges loại từ & kho */
    .pos-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-vocab { background-color: #E0F2FE; color: #0369A1; }
    .badge-colloc { background-color: #F3E8FF; color: #7E22CE; }
    
    .pos-tag {
        font-size: 0.85rem;
        color: #64748B;
        font-style: italic;
        margin-left: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div>
    <div class="app-title">Sample Vocabulary Library</div>
    <div class="app-subtitle">Khám phá kho từ vựng mẫu theo từng chủ đề và thêm nhanh các từ cần học vào bộ sưu tập cá nhân</div>
</div>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Đọc kho từ vựng mẫu và kho cá nhân của user
sample_data = load_data("sample_words.json")
user_colloc = load_data(f"data_collocation_{username}.json")
user_vocab = load_data(f"data_vocab_{username}.json")

if not isinstance(user_colloc, dict): user_colloc = {}
if not isinstance(user_vocab, dict): user_vocab = {}
user_all_words = {**user_colloc, **user_vocab}

if not sample_data:
    st.info("Chưa có từ vựng mẫu nào trong thư viện. Vui lòng kiểm tra lại file sample_words.json!")
    st.stop()

# --- 1. LỌC CÁC CHỦ ĐỀ (TOPICS) ---
topics = sorted(list(set(item.get("topic", "Khác") for item in sample_data.values() if isinstance(item, dict))))

st.write("**Chọn chủ đề bài học:**")
selected_topic = st.radio("Chủ đề:", topics, horizontal=True, label_visibility="collapsed")

st.divider()

# --- 2. HIỂN THỊ TỪ VỰNG DẠNG LƯỚI CARD ---
topic_words = {
    w: item for w, item in sample_data.items()
    if isinstance(item, dict) and item.get("topic") == selected_topic
}

st.caption(f"Chủ đề **{selected_topic}** hiện có **{len(topic_words)}** từ vựng mẫu:")

if not topic_words:
    st.info("Chưa có từ vựng nào thuộc chủ đề này.")
else:
    items = list(topic_words.items())
    cols_per_row = 2  # Chia làm 2 cột Card song song
    
    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(items):
                word, item = items[i + j]
                meaning = item.get("meaning", "")
                w_type = item.get("type", "vocab")
                pos_tag = item.get("pos", "")

                badge_class = "badge-colloc" if w_type == "collocation" else "badge-vocab"
                badge_label = "Collocation" if w_type == "collocation" else "Vocab"
                pos_html = f"<span class='pos-tag'>({pos_tag})</span>" if pos_tag else ""

                with cols[j]:
                    # Render Thẻ Card
                    st.markdown(f"""
                    <div class="sample-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span class="sample-word">{word}</span> {pos_html}
                            </div>
                            <span class="pos-badge {badge_class}">{badge_label}</span>
                        </div>
                        <div class="sample-meaning">{meaning}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Nút bấm hành động
                    if word in user_all_words:
                        st.success("✓ Đã có trong bộ học", icon="✅")
                    else:
                        if st.button("➕ Thêm vào bộ học", key=f"lib_add_{word}", type="primary", use_container_width=True):
                            target_file = f"data_collocation_{username}.json" if w_type == "collocation" else f"data_vocab_{username}.json"
                            user_repo = load_data(target_file)
                            if not isinstance(user_repo, dict): user_repo = {}

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
