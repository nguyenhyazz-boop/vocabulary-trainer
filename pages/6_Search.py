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
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library | Vocabulary Trainer", page_icon="📚", layout="wide")

# --- CUSTOM CSS: BỘ BỘ LƯỚI THẺ TỪ VỰNG CHUẨN MODERN UI ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    /* Header & Subtitle */
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

    /* Vocab Card styling */
    .vocab-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
        transition: all 0.2s ease-in-out;
        height: 100%;
    }
    .vocab-card:hover {
        border-color: #CBD5E1;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }
    .vocab-word {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0F172A;
    }
    .vocab-meaning {
        font-size: 1rem;
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
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-noun { background-color: #E0F2FE; color: #0369A1; }
    .badge-verb { background-color: #DCFCE7; color: #15803D; }
    .badge-adj { background-color: #FEF9C3; color: #A16207; }
    .badge-adv { background-color: #F3E8FF; color: #7E22CE; }
    .badge-phrase { background-color: #FFEDD5; color: #C2410C; }
    .badge-other { background-color: #F1F5F9; color: #475569; }

    .stats-tag {
        font-size: 0.75rem;
        color: #94A3B8;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div>
    <div class="app-title">Vocabulary Library</div>
    <div class="app-subtitle">Quản lý, tra cứu và theo dõi tiến độ ghi nhớ toàn bộ từ vựng cá nhân</div>
</div>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
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

    # Kiểm tra khớp từ khóa
    match_query = search_query in word or search_query in meaning
    # Kiểm tra khớp loại từ
    match_pos = (filter_pos == "Tất cả") or (filter_pos.lower() == pos.lower())

    if match_query and match_pos:
        filtered_words[word] = info

st.caption(f"Hiển thị **{len(filtered_words)}** / {len(combined_data)} từ vựng")

if not filtered_words:
    st.info("Không tìm thấy từ vựng nào phù hợp!")
else:
    # --- HIỂN THỊ DẠNG GRID (LƯỚI 3 CỘT) ---
    items = list(filtered_words.items())
    
    # Chia lưới 3 cột
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
                    # Vẽ Card
                    ex_html = f'<div class="vocab-example">"{example}"</div>' if example else ""
                    st.markdown(f"""
                    <div class="vocab-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="vocab-word">{word}</span>
                            <span class="pos-badge {badge_class}">{pos}</span>
                        </div>
                        <div class="vocab-meaning">{meaning}</div>
                        {ex_html}
                        <div class="stats-tag">🎯 Đúng: {correct} | ❌ Sai: {wrong}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Nút thao tác nhỏ gọn bên dưới card
                    with st.popover("⚙️ Thao tác"):
                        if st.button("🗑️ Xóa từ này", key=f"del_{word}", use_container_width=True):
                            target_file = info["repo"]
                            repo_dict = vocab_data if target_file == vocab_file else colloc_data
                            if word in repo_dict:
                                del repo_dict[word]
                                save_data(repo_dict, target_file)
                                st.success(f"Đã xóa '{word}'")
                                st.rerun()
