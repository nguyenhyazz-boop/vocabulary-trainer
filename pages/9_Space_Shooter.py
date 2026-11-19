import json
import os
import random
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
from utils.data_manager import load_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Space Shooter | Vocabulary Trainer", page_icon="📖", layout="wide")
apply_global_theme("9_Space_Shooter")

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception:
        return None

supabase = get_supabase()

def get_leaderboard():
    if not supabase:
        return []
    try:
        res = supabase.table("space_leaderboard").select("*").order("high_score", desc=True).limit(10).execute()
        return res.data or []
    except Exception:
        return []

st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.5rem;
        max-width: 960px !important;
    }
    .space-header {
        text-align: center;
        margin-bottom: 1.3rem;
    }
    .space-sub {
        font-size: 0.8rem;
        font-weight: 700;
        color: #78716C;
        letter-spacing: 0.7px;
        text-transform: uppercase;
    }
    .space-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }
    .space-desc {
        color: #57534E;
        font-size: 0.94rem;
        margin-top: 4px;
    }

    /* Bảng xếp hạng Warm Editorial */
    .lb-card {
        background-color: #EFECE3;
        border: 1px solid #E5DFD2;
        border-radius: 18px;
        padding: 12px 16px;
        margin-top: 10px;
    }
    .lb-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-size: 0.92rem;
        color: #1C1917;
    }
    .lb-row:last-child {
        margin-bottom: 0;
    }
    .lb-rank-badge {
        display: inline-block;
        background-color: #F3EFE6;
        color: #57534E;
        font-size: 0.78rem;
        font-weight: 800;
        padding: 2px 9px;
        border-radius: 20px;
        margin-right: 8px;
    }
    .lb-rank-top {
        background-color: #FACC15;
        color: #1C1917;
    }
    .lb-me {
        border-color: #7C3AED !important;
        background-color: #FAF5FF !important;
    }
    .lb-score-pill {
        background-color: #EFECE3;
        color: #1C1917;
        font-size: 0.8rem;
        font-weight: 800;
        padding: 3px 10px;
        border-radius: 20px;
    }

    /* Tag từ đã chọn dịu mắt theo tông Editorial */
    span[data-baseweb="tag"] {
        background-color: #EFECE3 !important;
        color: #1C1917 !important;
        border: 1px solid #DFD9C8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] span {
        color: #1C1917 !important;
    }
    span[data-baseweb="tag"] svg {
        fill: #57534E !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="space-header">
    <div class="space-sub">Arcade Vocabulary Reflex</div>
    <div class="space-title">Space Vocab Defender</div>
    <div class="space-desc">Bắn hạ hạm đội tàu địch bằng từ vựng tiếng Anh — Kỷ lục tự động cập nhật lên Bảng Xếp Hạng</div>
</div>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username

with st.expander("Top 10 Pilots Leaderboard", expanded=False):
    col_lb1, col_lb2 = st.columns([4, 1])
    with col_lb1:
        st.caption("Kỷ lục cá nhân cao nhất của bạn sẽ tự động cập nhật ngay khi kết thúc trận đấu.")
    with col_lb2:
        if st.button("Refresh Top", use_container_width=True):
            st.rerun()

    lb_data = get_leaderboard()
    if not lb_data:
        st.info("Chưa có ai ghi danh trên Bảng Xếp Hạng. Hãy chơi ngay 1 trận để mở bát!")
    else:
        rows_html = ""
        for idx, row in enumerate(lb_data):
            rank_num = idx + 1
            rank_cls = "lb-rank-badge lb-rank-top" if rank_num <= 3 else "lb-rank-badge"
            u_name = str(row.get("username", "Unknown"))
            h_score = int(row.get("high_score", 0) or 0)
            m_combo = int(row.get("max_combo", 0) or 0)
            me_cls = " lb-me" if u_name == username else ""
            rows_html += (
                f'<div class="lb-row{me_cls}">'
                f'<div><span class="{rank_cls}">#{rank_num}</span><b>{u_name}</b></div>'
                f'<div style="display:flex; gap:8px; align-items:center;">'
                f'<span style="font-size:0.82rem; color:#78716C; font-weight:700;">Combo x{m_combo}</span>'
                f'<span class="lb-score-pill">{h_score:,} pts</span>'
                f'</div>'
                f'</div>'
            )
        st.markdown(f'<div class="lb-card">{rows_html}</div>', unsafe_allow_html=True)

vocab_data = load_data(f"data_vocab_{username}.json")
colloc_data = load_data(f"data_collocation_{username}.json")

if not isinstance(vocab_data, dict):
    vocab_data = {}
if not isinstance(colloc_data, dict):
    colloc_data = {}

with st.expander("Squadron & Game Settings", expanded=True):
    col1, col2, col3 = st.columns(3, gap="medium")

    with col1:
        source_choice = st.selectbox(
            "Nguồn từ vựng:",
            ["Normal Vocabulary", "Collocations & Phrases", "Tất cả từ đã lưu", "Chỉ từ hay sai (Wrong > 0)"]
        )
    with col2:
        game_mode = st.selectbox(
            "Chế độ hiển thị:",
            ["Thường (Có gợi ý khung chữ)", "Thử thách (Chỉ hiện nghĩa Việt)"]
        )
    with col3:
        difficulty = st.selectbox(
            "Tốc độ tàu địch:",
            ["Chậm (Khởi động)", "Trung bình (Chuẩn)", "Nhanh (Phản xạ cao)"]
        )

    pool = {}
    if source_choice == "Normal Vocabulary":
        pool = vocab_data
    elif source_choice == "Collocations & Phrases":
        pool = colloc_data
    elif source_choice == "Tất cả từ đã lưu":
        pool = {**vocab_data, **colloc_data}
    else:
        combined = {**vocab_data, **colloc_data}
        pool = {k: v for k, v in combined.items() if isinstance(v, dict) and v.get("wrong", 0) > 0}

    all_keys = list(pool.keys())
    if not all_keys:
        st.info("Kho từ vựng bạn chọn hiện đang trống! Hãy thêm từ ở mục Library hoặc Add Word trước nhé.")
        st.stop()

    select_type = st.radio(
        "Cách chọn từ đưa vào trận:",
        ["Rút ngẫu nhiên theo số lượng", "Tự chọn từng từ muốn ôn"],
        horizontal=True
    )

    selected_words = []
    if select_type == "Rút ngẫu nhiên theo số lượng":
        max_w = min(50, len(all_keys))
        if max_w <= 1:
            num_words = max_w
            st.info(f"Kho hiện chỉ có **{num_words}** từ, hệ thống sẽ đưa toàn bộ vào trận!")
        else:
            num_words = st.slider(
                "Số lượng tàu địch (từ vựng):",
                min_value=1,
                max_value=max_w,
                value=min(15, max_w)
            )
        if st.button("Shuffle Word Pool"):
            st.session_state.space_seed = random.randint(1, 99999)
        seed = st.session_state.get("space_seed", 42)
        rng = random.Random(seed)
        selected_words = rng.sample(all_keys, num_words)
    else:
        selected_words = st.multiselect(
            "Chọn các từ bạn muốn đưa vào màn chơi:",
            options=all_keys,
            default=all_keys[:min(10, len(all_keys))]
        )

if not selected_words:
    st.warning("Vui lòng chọn ít nhất 1 từ vựng để bắt đầu!")
    st.stop()

game_words = []
for w in selected_words:
    info = pool[w]
    meaning = info.get("meaning", str(info)) if isinstance(info, dict) else str(info)
    game_words.append({
        "en": w.strip(),
        "vi": meaning.strip()
    })

speed_map = {
    "Chậm (Khởi động)": 0.35,
    "Trung bình (Chuẩn)": 0.6,
    "Nhanh (Phản xạ cao)": 0.95
}

config_payload = json.dumps({
    "words": game_words,
    "speed": speed_map[difficulty],
    "hint": "Thường" in game_mode,
    "player": username,
    "sb_url": SUPABASE_URL,
    "sb_key": SUPABASE_KEY
}, ensure_ascii=False)

if not os.path.exists("space_game.html"):
    st.error("Không tìm thấy file space_game.html ở thư mục gốc!")
    st.stop()

with open("space_game.html", "r", encoding="utf-8") as f:
    raw_html = f.read()

final_html = raw_html.replace("__GAME_CONFIG__", config_payload)
components.html(final_html, height=630)
