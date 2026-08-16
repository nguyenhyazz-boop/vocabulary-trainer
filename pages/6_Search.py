import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Search & Edit | Vocabulary Trainer", page_icon="🔍", layout="wide")

# --- CUSTOM CSS: MODERN SAAS SEARCH & CARD STYLING ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1050px;
    }
    
    /* Header & Subtitle */
    .app-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* SVG Icon Inline Base */
    .svg-icon {
        display: inline-block;
        width: 18px;
        height: 18px;
        vertical-align: -3px;
        fill: currentColor;
    }

    /* Vocab Card styling */
    .vocab-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease-in-out;
    }
    .vocab-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }
    .vocab-word {
        font-size: 1.2rem;
        font-weight: 700;
        color: #0F172A;
    }
    .vocab-meaning {
        font-size: 0.95rem;
        color: #334155;
        font-weight: 500;
        margin-top: 6px;
    }
    .vocab-example {
        font-size: 0.85rem;
        color: #64748B;
        font-style: italic;
        margin-top: 8px;
        padding-left: 8px;
        border-left: 2px solid #E2E8F0;
    }

    /* Badges */
    .pos-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }
    .badge-noun { background-color: #E0F2FE; color: #0369A1; }
    .badge-verb { background-color: #DCFCE7; color: #15803D; }
    .badge-adj { background-color: #FEF9C3; color: #A16207; }
    .badge-adv { background-color: #F3E8FF; color: #7E22CE; }
    .badge-phrase { background-color: #FFEDD5; color: #C2410C; }
    .badge-other { background-color: #F1F5F9; color: #475569; }

    /* Thống kê tỷ lệ nhớ */
    .stats-container {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 12px;
        padding-top: 8px;
        border-top: 1px dashed #F1F5F9;
    }
</style>
""", unsafe_allow_html=True)

# --- SVG ICONS ---
ICON_SEARCH = '<svg class="svg-icon" viewBox="0 0 24 24"><path d="M10 2a8 8 0 0 1 6.32 12.906l4.387 4.387a1 1 0 0 1-1.414 1.414l-4.387-4.387A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>'

# --- HEADER ---
st.markdown(f"""
<div>
    <div class="app-title">{ICON_SEARCH} Search & Edit</div>
    <div class="app-subtitle">Tra cứu từ vựng cá nhân, chỉnh sửa nghĩa hoặc quản lý kho từ vựng</div>
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
    search_query = st.text_input("Tìm kiếm từ vựng hoặc nghĩa...", placeholder="Type to search...").strip().lower()

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
    # --- HIỂN THỊ DẠNG GRID (LƯỚI 3 CỘT) ---
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

                # Badge màu sắc
                pos_key = pos.lower()
                badge_class = f"badge-{pos_key}" if pos_key in ["noun", "verb", "adj", "adv", "phrase"] else "badge-other"

                with cols[j]:
                    ex_html = f'<div class="vocab-example">"{example}"</div>' if example else ""
                    
                    # SỬA DỨT ĐIỂM TẠI ĐÂY: Render HTML sạch sẽ không bị đè lỗi
                    st.markdown(f"""
                    <div class="vocab-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="vocab-word">{word}</span>
                            <span class="pos-badge {badge_class}">{pos}</span>
                        </div>
                        <div class="vocab-meaning">{meaning}</div>
                        {ex_html}
                        <div class="stats-container">
                            <span>Đúng: <b>{correct}</b></span>
                            <span>|</span>
                            <span>Sai: <b>{wrong}</b></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Popover thao tác tối giản
                    with st.popover("Thao tác"):
                        if st.button("Xóa từ này", key=f"del_{word}", use_container_width=True, type="secondary"):
                            target_file = info["repo"]
                            repo_dict = vocab_data if target_file == vocab_file else colloc_data
                            if word in repo_dict:
                                del repo_dict[word]
                                save_data(repo_dict, target_file)
                                st.success(f"Đã xóa '{word}'")
                                st.rerun()
