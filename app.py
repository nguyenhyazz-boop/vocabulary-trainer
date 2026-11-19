import streamlit as st
from supabase import create_client
from utils.data_manager import load_data, register_user, authenticate_user
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Vocabulary Trainer | Dashboard", page_icon="📖", layout="wide")
apply_global_theme("dashboard")

# --- KẾT NỐI SUPABASE ---
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

def fetch_space_stats(current_user: str):
    if not supabase:
        return 0, []
    try:
        res = supabase.table("space_leaderboard").select("*").order("high_score", desc=True).limit(5).execute()
        top_list = res.data or []
        user_best = 0
        for row in top_list:
            if row.get("username") == current_user:
                user_best = row.get("high_score", 0)
                break
        if user_best == 0:
            u_res = supabase.table("space_leaderboard").select("high_score").eq("username", current_user).execute()
            if u_res.data:
                user_best = u_res.data[0].get("high_score", 0)
        return user_best, top_list
    except Exception:
        return 0, []

# --- CUSTOM EDITORIAL CSS CHO DASHBOARD ---
st.markdown("""
<style>
    .top-bar {
        display: flex;
        justify-content: flex-end;
        gap: 10px;
        margin-bottom: 14px;
    }
    .stat-pill {
        background: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 20px;
        padding: 5px 14px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #1C1917;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .dot-orange { width: 8px; height: 8px; border-radius: 50%; background: #EA580C; display: inline-block; }
    .dot-purple { width: 8px; height: 8px; border-radius: 50%; background: #7C3AED; display: inline-block; }

    /* Hero Card kiểu Filko */
    .editorial-hero {
        background-color: #EFECE3;
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 24px;
        border: 1px solid #E5DFD2;
    }
    .hero-greeting {
        font-size: 0.95rem;
        font-weight: 500;
        color: #57534E;
        margin-bottom: 8px;
    }
    .hero-headline {
        font-size: 2.15rem;
        font-weight: 800;
        color: #1C1917;
        line-height: 1.18;
        letter-spacing: -0.6px;
        margin-bottom: 18px;
    }

    /* 3 Thẻ dọc 01 - 02 - 03 */
    .module-card {
        border-radius: 16px;
        padding: 18px;
        height: 185px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease;
    }
    .module-card:hover {
        transform: translateY(-3px);
    }
    .mod-cream {
        background-color: #FAF8F2;
        color: #1C1917;
        border: 1px solid #E5DFD2;
    }
    .mod-yellow {
        background-color: #FACC15;
        color: #1C1917;
    }
    .mod-purple {
        background-color: #7C3AED;
        color: #FFFFFF;
    }
    .mod-num {
        font-size: 0.8rem;
        font-weight: 700;
        opacity: 0.75;
    }
    .mod-title {
        font-size: 1.15rem;
        font-weight: 800;
        line-height: 1.25;
        margin-top: 6px;
    }
    .mod-meta {
        font-size: 0.82rem;
        font-weight: 600;
        opacity: 0.85;
    }

    /* Danh sách Module tiến độ bên dưới */
    .row-item {
        background: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 14px;
        padding: 14px 18px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .row-title {
        font-size: 0.98rem;
        font-weight: 700;
        color: #1C1917;
    }
    .row-desc {
        font-size: 0.83rem;
        color: #78716C;
    }

    /* Thẻ Leaderboard bên phải */
    .schedule-card {
        background: #EFECE3;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 10px;
        border: 1px solid #E5DFD2;
    }
    .tag-pill {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 700;
        color: #1C1917;
        display: inline-block;
        margin-top: 6px;
    }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==============================================================================
# ĐÃ ĐĂNG NHẬP -> DASHBOARD WARM EDITORIAL
# ==============================================================================
if st.session_state.logged_in:
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1.4rem;
            padding-bottom: 3rem;
            max-width: 1120px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    username = st.session_state.username

    vocab_data = load_data(f"data_vocab_{username}.json")
    colloc_data = load_data(f"data_collocation_{username}.json")
    if not isinstance(vocab_data, dict):
        vocab_data = {}
    if not isinstance(colloc_data, dict):
        colloc_data = {}

    total_vocab = len(vocab_data)
    total_colloc = len(colloc_data)
    total_all = total_vocab + total_colloc

    all_items = list(vocab_data.values()) + list(colloc_data.values())
    total_correct = sum(v.get("correct", 0) for v in all_items if isinstance(v, dict))
    total_wrong = sum(v.get("wrong", 0) for v in all_items if isinstance(v, dict))
    total_attempts = total_correct + total_wrong
    accuracy = round((total_correct / total_attempts) * 100) if total_attempts > 0 else 0

    user_high_score, leaderboard = fetch_space_stats(username)

    # Top Stats Pills giống góc trên bên phải của mẫu
    st.markdown(f"""
    <div class="top-bar">
        <span class="stat-pill"><span class="dot-orange"></span> {user_high_score:,} XP</span>
        <span class="stat-pill"><span class="dot-purple"></span> {total_all} words</span>
    </div>
    """, unsafe_allow_html=True)

    # Khối Hero chính chia 2 nửa: Trái (Tiến độ + Nút đen) | Phải (3 Thẻ 01 - 02 - 03)
    st.markdown('<div class="editorial-hero">', unsafe_allow_html=True)
    col_left, col_right = st.columns([1.05, 1.45], gap="large")

    with col_left:
        st.markdown(f"""
        <div class="hero-greeting">Salut, {username}!</div>
        <div class="hero-headline">You've stored<br>{total_all} words<br>in your vault</div>
        """, unsafe_allow_html=True)
        if st.button("Start Practice  ↗", type="primary"):
            st.switch_page("pages/1_study.py")

    with col_right:
        c1, c2, c3 = st.columns(3, gap="small")
        with c1:
            st.markdown(f"""
            <div class="module-card mod-cream">
                <div>
                    <div class="mod-num">01</div>
                    <div class="mod-title">Core<br>Vocabulary</div>
                </div>
                <div class="mod-meta">{total_vocab} words</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="module-card mod-yellow">
                <div>
                    <div class="mod-num">02</div>
                    <div class="mod-title">Phrases &<br>Collocations</div>
                </div>
                <div class="mod-meta">{total_colloc} items</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="module-card mod-purple">
                <div>
                    <div class="mod-num">03</div>
                    <div class="mod-title">Memory<br>Accuracy</div>
                </div>
                <div class="mod-meta">{accuracy}% score</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Khu vực bên dưới chia 2 cột: Trái (Lộ trình & Lối tắt) | Phải (Top Space Leaderboard)
    col_main, col_side = st.columns([1.65, 1], gap="large")

    with col_main:
        st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:8px;">
            <div>
                <div style="font-size:0.8rem; color:#78716C; font-weight:600;">Training Overview</div>
                <div style="font-size:1.25rem; font-weight:800; color:#1C1917;">Learning Modules</div>
            </div>
            <div style="font-size:0.9rem; font-weight:700; color:#7C3AED;">{accuracy}% Mastery</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(min(accuracy / 100, 1.0))
        st.write("")

        # 4 hàng lối tắt gọn gàng
        r1, b1 = st.columns([3.5, 1])
        with r1:
            st.markdown("""
            <div class="row-item">
                <div>
                    <div class="row-title">Smart Add Word</div>
                    <div class="row-desc">Auto-detect part of speech, Vietnamese meaning & examples</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b1:
            st.write("")
            if st.button("Open", key="btn_add", use_container_width=True):
                st.switch_page("pages/4_Add_Word.py")

        r2, b2 = st.columns([3.5, 1])
        with r2:
            st.markdown("""
            <div class="row-item">
                <div>
                    <div class="row-title">AI Context Reader</div>
                    <div class="row-desc">Generate stories & dialogues from your personal word list</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b2:
            st.write("")
            if st.button("Open", key="btn_ai", use_container_width=True):
                st.switch_page("pages/8_🤖_AI_Reader.py")

        r3, b3 = st.columns([3.5, 1])
        with r3:
            st.markdown("""
            <div class="row-item">
                <div>
                    <div class="row-title">YouTube Video Vocab</div>
                    <div class="row-desc">Extract subtitles and save words from any English video</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b3:
            st.write("")
            if st.button("Open", key="btn_vid", use_container_width=True):
                st.switch_page("pages/10_🎬_Video_Vocab.py")

        r4, b4 = st.columns([3.5, 1])
        with r4:
            st.markdown("""
            <div class="row-item">
                <div>
                    <div class="row-title">Space Vocab Shooter</div>
                    <div class="row-desc">Defend your ship by typing translations at high speed</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with b4:
            st.write("")
            if st.button("Play", key="btn_space", use_container_width=True, type="primary"):
                st.switch_page("pages/9_🚀_Space_Shooter.py")

    with col_side:
        st.markdown("""
        <div style="font-size:1.25rem; font-weight:800; color:#1C1917; margin-bottom:12px;">Top Pilots</div>
        """, unsafe_allow_html=True)

        if leaderboard:
            for idx, row in enumerate(leaderboard[:4], start=1):
                dot_color = "#7C3AED" if idx == 1 else ("#EA580C" if idx == 2 else "#16A34A")
                st.markdown(f"""
                <div class="schedule-card">
                    <div style="font-size:0.75rem; color:#78716C; font-weight:600;">Rank #{idx}</div>
                    <div style="font-size:1rem; font-weight:800; color:#1C1917; margin-top:2px;">{row.get('username', '')}</div>
                    <div style="font-size:0.82rem; color:#57534E;">Max Combo x{row.get('max_combo', 0)}</div>
                    <span class="tag-pill"><span style="color:{dot_color};">●</span> {row.get('high_score', 0):,} pts</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Chưa có dữ liệu bảng xếp hạng.")

# ==============================================================================
# CHƯA ĐĂNG NHẬP -> LANDING WARM EDITORIAL
# ==============================================================================
else:
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            max-width: 960px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    col_intro, col_auth = st.columns([1.15, 1], gap="large")

    with col_intro:
        st.markdown("""
        <div class="editorial-hero" style="margin-bottom: 16px;">
            <div class="hero-greeting">Personal EdTech Workspace</div>
            <div class="hero-headline">Master English<br>vocabulary<br>effortlessly.</div>
            <div style="font-size:0.95rem; color:#57534E; line-height:1.5;">
                Tích hợp trợ lý AI tự phân tích từ vựng, bóc phụ đề YouTube và game bắn tàu phản xạ tốc độ cao.
            </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="module-card mod-yellow" style="height: 130px;">
                <div class="mod-num">01</div>
                <div class="mod-title">AI Auto-Analyze & Context Reader</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="module-card mod-purple" style="height: 130px;">
                <div class="mod-num">02</div>
                <div class="mod-title">YouTube Subtitles & Space Arcade</div>
            </div>
            """, unsafe_allow_html=True)

    with col_auth:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

            with tab_login:
                st.subheader("Welcome back")
                login_user = st.text_input("Username", key="login_user_input", placeholder="Enter your username")
                login_pass = st.text_input("Password", type="password", key="login_pass_input", placeholder="Enter your password")

                st.write("")
                if st.button("Sign In  ↗", use_container_width=True, type="primary"):
                    if not login_user or not login_pass:
                        st.warning("Vui lòng nhập đầy đủ thông tin!")
                    else:
                        if authenticate_user(login_user, login_pass):
                            st.session_state.logged_in = True
                            st.session_state.username = login_user
                            st.rerun()
                        else:
                            st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

            with tab_register:
                st.subheader("New Account")
                reg_user = st.text_input("Choose a username", key="reg_user_input")
                reg_pass = st.text_input("Password", type="password", key="reg_pass_input")
                reg_pass_confirm = st.text_input("Confirm password", type="password", key="reg_confirm_input")

                st.write("")
                if st.button("Create Account", use_container_width=True, type="primary"):
                    if not reg_user or not reg_pass:
                        st.warning("Vui lòng điền đầy đủ thông tin!")
                    elif reg_pass != reg_pass_confirm:
                        st.error("Mật khẩu xác nhận không khớp!")
                    else:
                        success, msg = register_user(reg_user, reg_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)
