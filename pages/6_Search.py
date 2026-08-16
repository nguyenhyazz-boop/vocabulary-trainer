import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Search & Edit | Vocabulary Trainer", page_icon="🔍", layout="wide")

# --- CUSTOM CSS: ORGANIC & CHILL SAAS STYLING ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1050px;
    }
    
    /* Header & Subtitle */
    .app-title {
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.9rem;
        margin-bottom: 1.5rem;
    }

    /* SVG Icon Inline Base */
    .svg-icon {
        display: inline-block;
        width: 16px;
        height: 16px;
        vertical-align: -2px;
        fill: currentColor;
    }

    /* Badges Tinh Tế */
    .pos-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .badge-noun { background-color: #F1F5F9; color: #475569; }
    .badge-verb { background-color: #F1F5F9; color: #475569; }
    .badge-adj { background-color: #F1F5F9; color: #475569; }
    .badge-adv { background-color: #F1F5F9; color: #475569; }
    .badge-phrase { background-color: #F1F5F9; color: #475569; }
    .badge-other { background-color: #F1F5F9; color: #475569; }

    /* Stats Line Chill */
    .stats-line {
        font-size: 0.8rem;
        color: #94A3B8;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 6px;
    }
    .dot-separator {
        display: inline-block;
        width: 4px;
        height: 4px;
        background-color: #CBD5E1;
        border-radius: 50%;
    }
</style>
""", unsafe_allow_html=True)

# --- SVG ICONS TỐI GIẢN ---
ICON_SEARCH = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M10 2a8 8 0 0 1 6.32 12.906l4.387 4.387a1 1 0 0 1-1.414 1.414l-4.387-4.387A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>'

# --- HEADER ---
st.markdown(f"""
<div>
    <div class="app-title">{ICON_SEARCH} Search & Edit</div>
    <div class="app-subtitle">Tra cứu từ vựng cá nhân và quản lý kho dữ liệu</div>
</div>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# --- ĐỌC DỮ LIỆU ---
vocab_file = f"data_vocab_{username}.json"
colloc_file = f"data_collocation_{username}.json"

vocab_data = load_data(vocab_file)
if not isinstance(vocab_data, dict): vocab_data = {}

colloc_data = load_data(colloc_file)
if not isinstance(colloc_data, dict): colloc_data = {}

# --- THANH TÌM KIẾM VÀ BỘ LỌC ---
col_search, col_filter, col_repo = st.columns([3, 1.5, 1.5])

with col_search:
    search_query = st.text_input("Tìm kiếm từ vựng hoặc nghĩa...", placeholder="Nhập từ cần tìm...").strip().lower()

with col_filter:
    filter_pos = st.selectbox("Loại từ", ["Tất cả", "Noun", "Verb", "Adj", "Adv", "Phrase", "Other"])

with col_repo:
    selected_repo = st.selectbox("Kho từ", ["Tất cả", "Normal Vocab", "Collocations"])

st.divider()

# Xử lý tổng hợp từ vựng
combined_data = {}

if selected_repo in ["Tất cả", "Normal Vocab"]:
    for k, v in vocab_data.items():
        combined_data[k] = {**v, "repo": vocab_file}

if selected_repo in ["Tất cả", "Collocations"]:
    for k, v in colloc_data.items():
        combined_data[k] = {**v, "repo": colloc_file}

# Lọc theo từ khóa tìm kiếm và Loại từ
filtered_words = {}
for word, info in combined_data.items():
    meaning = info.get("meaning", "").lower()
    pos = info.get("pos", "Other")

    match_query = search_query in word or search_query in meaning
    match_pos = (filter_pos == "Tất cả") or (filter_pos.lower() == pos.lower())

    if match_query and match_pos:
        filtered_words[word] = info

st.caption(f"Hiển thị **{len(filtered_words)}** / {len(combined_data)} từ vựng")

if not filtered_words:
    st.info("Không tìm thấy từ vựng nào phù hợp!")
else:
    items = list(filtered_words.items())
    
    cols_per_row = 3
    for i in range(0, len(items), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(items):
                word, info = items[i + j]
                pos = info.get("pos", "Other")
                meaning = info.get("meaning", "N/A")
                example = info.get("example", "")
                correct = info.get("correct", 0)
                wrong = info.get("wrong", 0)

                pos_key = pos.lower()
                badge_class = f"badge-{pos_key}" if pos_key in ["noun", "verb", "adj", "adv", "phrase"] else "badge-other"

                with cols[j]:
                    with st.container(border=True):
                        # Header Từ vựng & Tag Loại từ tối giản
                        st.markdown(f"""
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">{word}</span>
                            <span class="pos-badge {badge_class}">{pos}</span>
                        </div>
                        <div style="font-size: 0.95rem; color: #475569; font-weight: 500; margin-top: 4px;">{meaning}</div>
                        """, unsafe_allow_html=True)

                        if example:
                            st.caption(f'"{example}"')

                        # Thống kê Đúng/Sai kiểu Minimalist Chill
                        st.markdown(f"""
                        <div class="stats-line">
                            <span>Đúng {correct}</span>
                            <span class="dot-separator"></span>
                            <span>Sai {wrong}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        # Popover Thao tác gọn gàng
                        with st.popover("Thao tác", use_container_width=True):
                            if st.button("Xóa từ này", key=f"del_{word}", use_container_width=True):
                                target_file = info["repo"]
                                repo_dict = vocab_data if target_file == vocab_file else colloc_data
                                if word in repo_dict:
                                    del repo_dict[word]
                                    save_data(repo_dict, target_file)
                                    st.success(f"Đã xóa '{word}'")
                                    st.rerun()
