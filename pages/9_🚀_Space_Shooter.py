import json
import random
import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client
from utils.data_manager import load_data

st.set_page_config(page_title="Space Shooter | Vocabulary Trainer", page_icon="🚀", layout="wide")

# --- LẤY THÔNG TIN SUPABASE ---
SUPABASE_URL = ""
SUPABASE_KEY = ""
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
except Exception:
    pass

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

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 920px !important;
    }
    .app-title {
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        color: #1E293B;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        text-align: center;
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.2rem;
    }
    .lb-card {
        background: linear-gradient(135deg, #0F172A, #1E293B);
        color: #F8FAFC;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 10px;
        border: 1px solid #334155;
    }
    .lb-row {
        display: flex;
        justify-content: space-between;
        padding: 7px 10px;
        border-bottom: 1px solid rgba(148, 163, 184, 0.15);
        font-size: 0.94rem;
    }
    .lb-row:last-child { border-bottom: none; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🚀 Space Vocab Defender</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Bắn hạ hạm đội tàu địch bằng từ vựng tiếng Anh — Kỷ lục tự động cập nhật lên Bảng Xếp Hạng!</div>', unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# --- BẢNG XẾP HẠNG TOP 10 (TỰ ĐỘNG ĐỒNG BỘ) ---
with st.expander("🏆 Bảng Xếp Hạng Top 10 Phi Công Vũ Trụ", expanded=False):
    col_lb1, col_lb2 = st.columns([4, 1])
    with col_lb1:
        st.caption("Kỷ lục cá nhân cao nhất của bạn sẽ tự động cập nhật ngay khi kết thúc trận đấu.")
    with col_lb2:
        if st.button("🔄 Làm mới Top", use_container_width=True):
            st.rerun()

    lb_data = get_leaderboard()
    if not lb_data:
        st.info("Chưa có ai ghi danh trên Bảng Xếp Hạng. Hãy chơi ngay 1 trận để mở bát!")
    else:
        medals = ["🥇", "🥈", "🥉"]
        rows_html = ""
        for idx, row in enumerate(lb_data):
            rank_icon = medals[idx] if idx < 3 else f"#{idx + 1}"
            u_name = row.get("username", "Unknown")
            h_score = row.get("high_score", 0)
            m_combo = row.get("max_combo", 0)
            highlight = "color: #38BDF8; font-weight: 700;" if u_name == username else ""
            rows_html += f"""
            <div class="lb-row" style="{highlight}">
                <span>{rank_icon} <b>{u_name}</b></span>
                <span>🔥 Combo x{m_combo}  |  ⭐ <b>{h_score:,} đ</b></span>
            </div>
            """
        st.markdown(f'<div class="lb-card">{rows_html}</div>', unsafe_allow_html=True)

# --- 1. TẢI DỮ LIỆU TỪ VỰNG CỦA USER ---
vocab_data = load_data(f"data_vocab_{username}.json")
colloc_data = load_data(f"data_collocation_{username}.json")

if not isinstance(vocab_data, dict):
    vocab_data = {}
if not isinstance(colloc_data, dict):
    colloc_data = {}

# --- 2. BẢNG THIẾT LẬP MÀN CHƠI ---
with st.expander("⚙️ Thiết lập đội hình & Chế độ chơi", expanded=True):
    col1, col2, col3 = st.columns(3)

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
        if st.button("🔄 Đổi bộ từ ngẫu nhiên khác"):
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
base_speed = str(speed_map[difficulty])
show_hint = "true" if "Thường" in game_mode else "false"
words_json = json.dumps(game_words, ensure_ascii=False)

# --- 3. GIAO DIỆN GAME VŨ TRỤ + TỰ ĐỘNG ĐỒNG BỘ SUPABASE ---
html_template = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
  body {
    background: #090D16;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: #F8FAFC;
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  #game-wrapper {
    position: relative;
    width: 100%;
    max-width: 840px;
    height: 610px;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid #1E293B;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
    background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
  }
  canvas {
    display: block;
    width: 100%;
    height: 100%;
  }
  #hud {
    position: absolute;
    top: 14px;
    left: 18px;
    right: 18px;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
    font-size: 14px;
    font-weight: 700;
    z-index: 5;
  }
  .hud-pill {
    background: rgba(15, 23, 42, 0.78);
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 6px 14px;
    border-radius: 999px;
    backdrop-filter: blur(4px);
  }
  #typing-bar {
    position: absolute;
    bottom: 62px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid #38BDF8;
    border-radius: 10px;
    padding: 5px 18px;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #38BDF8;
    min-width: 240px;
    text-align: center;
    z-index: 5;
  }
  #shop-bar {
    position: absolute;
    bottom: 12px;
    left: 16px;
    right: 16px;
    display: flex;
    justify-content: center;
    gap: 10px;
