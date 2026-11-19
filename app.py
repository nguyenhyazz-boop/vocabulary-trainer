import streamlit as st
from supabase import create_client
from utils.data_manager import load_data, register_user, authenticate_user
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Vocabulary Trainer | Dashboard", page_icon="📖", layout="wide")
apply_global_theme("dashboard")
# --- KẾT NỐI SUPABASE ĐỂ LẤY KỶ LỤC GAME ---
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

# --- GLOBAL DESIGN SYSTEM CSS ---
st.markdown("""
<style>
    /* Tùy chỉnh thanh Sidebar gọn gàng, hiện đại */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebarNav"] span {
        font-size: 0.98rem !important;
        font-weight: 600 !important;
        color: #334155;
    }
    [data-testid="stSidebarNav"] a {
        border-radius: 10px !important;
        margin: 2px 8px !important;
        padding: 8px 12px !important;
        transition: all 0.15s ease;
    }
    [data-testid="stSidebarNav"] a:hover {
        background-color: #EEF2FF !important;
        color: #4F46E5 !important;
    }

    /* Bo góc mềm mại cho toàn bộ nút bấm & input */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: transform 0.12s ease, box-shadow 0.12s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #4F46E5 0%, #2563EB 50%, #0284C7 100%);
        color: #FFFFFF;
        padding: 28px 32px;
        border-radius: 18px;
        margin-bottom: 1.6rem;
        box-shadow: 0 10px 25px rgba(79, 70, 229, 0.2);
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 6px;
        letter-spacing: -0.5px;
    }
    .hero-sub {
        font-size: 1rem;
        opacity: 0.92;
        line-height: 1.5;
    }

    /* Thẻ thống kê KPI */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        height: 100%;
    }
    .kpi-label {
        font-size: 0.82rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }
    .kpi-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        margin-top: 4px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #4F46E5;
        font-weight: 600;
        margin-top: 4px;
    }

    /* Thẻ tính năng điều hướng nhanh */
    .action-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    .action-card:hover {
        border-color: #818CF8;
        box-shadow: 0 6px 18px rgba(79, 70, 229, 0.08);
    }
    .action-icon {
        font-size: 1.6rem;
        margin-bottom: 6px;
    }
    .action-title {
        font-size: 1.05rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 4px;
    }
    .action-desc {
        font-size: 0.85rem;
        color: #64748B;
        line-height: 1.4;
        min-height: 38px;
    }

    /* Thẻ Landing Feature khi chưa đăng nhập */
    .feature-pill {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ==============================================================================
# TRẠNG THÁI 1: ĐÃ ĐĂNG NHẬP -> DASHBOARD TRUNG TÂM
# ==============================================================================
if st.session_state.logged_in:
    st.markdown("""
    <style>
        .main .block-container {
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1120px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    username = st.session_state.username

    # Tải dữ liệu cá nhân
    vocab_data = load_data(f"data_vocab_{username}.json")
    colloc_data = load_data(f"data_collocation_{username}.json")
    if not isinstance(vocab_data, dict):
        vocab_data = {}
    if not isinstance(colloc_data, dict):
        colloc_data = {}

    total_vocab = len(vocab_data)
    total_colloc = len(colloc_data)
    all_items = list(vocab_data.values()) + list(colloc_data.values())

    total_correct = sum(v.get("correct", 0) for v in all_items if isinstance(v, dict))
    total_wrong = sum(v.get("wrong", 0) for v in all_items if isinstance(v, dict))
    total_attempts = total_correct + total_wrong
    accuracy = round((total_correct / total_attempts) * 100) if total_attempts > 0 else 0

    user_high_score, leaderboard = fetch_space_stats(username)

    # Banner chào mừng
    col_hero, col_logout = st.columns([5, 1])
    with col_hero:
        st.markdown(f"""
        <div class="hero-banner">
            <div class="hero-title">👋 Chào mừng trở lại, {username}!</div>
            <div class="hero-sub">Sẵn sàng chinh phục mục tiêu từ vựng hôm nay chưa? Bạn đang sở hữu <b>{total_vocab + total_colloc}</b> từ & cụm từ trong kho cá nhân.</div>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.write("")
        st.write("")
        if st.button("🚪 Đăng xuất", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # Hàng 1: 4 Thẻ chỉ số KPI
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">📘 Từ đơn (Vocab)</div>
            <div class="kpi-value">{total_vocab}</div>
            <div class="kpi-sub">Từ vựng cốt lõi</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🧩 Collocations</div>
            <div class="kpi-value">{total_colloc}</div>
            <div class="kpi-sub">Cụm từ & Thành ngữ</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🎯 Độ chính xác</div>
            <div class="kpi-value">{accuracy}%</div>
            <div class="kpi-sub">{total_correct} lượt trả lời đúng</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">🚀 Kỷ lục Space</div>
            <div class="kpi-value">{user_high_score:,}</div>
            <div class="kpi-sub">Điểm cao nhất trên Top</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    st.subheader("⚡ Lối tắt luyện tập nhanh")

    # Hàng 2: 4 Thẻ điều hướng nhanh
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🧠</div>
            <div class="action-title">Ôn tập Flashcard</div>
            <div class="action-desc">Luyện trí nhớ chủ động và củng cố các từ hay sai.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vào ôn tập →", key="go_study", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📚_Study.py")

    with q2:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🚀</div>
            <div class="action-title">Space Shooter</div>
            <div class="action-desc">Bắn hạ hạm đội tàu địch bằng phản xạ gõ từ vựng.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Chơi ngay →", key="go_space", use_container_width=True):
            st.switch_page("pages/9_🚀_Space_Shooter.py")

    with q3:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">🎬</div>
            <div class="action-title">Video Vocab</div>
            <div class="action-desc">Dán link YouTube tiếng Anh để bóc lời thoại & nhặt từ.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Mở Video →", key="go_video", use_container_width=True):
            st.switch_page("pages/10_🎬_Video_Vocab.py")

    with q4:
        st.markdown("""
        <div class="action-card">
            <div class="action-icon">✨</div>
            <div class="action-title">Thêm từ với AI</div>
            <div class="action-desc">Nhập từ mới, AI tự dịch nghĩa và tạo câu ví dụ chuẩn.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Thêm từ mới →", key="go_add", use_container_width=True):
            st.switch_page("pages/4_📝_Add_Word.py")

    # Hàng 3: Vinh danh Top Phi Công Vũ Trụ ngay trang chủ
    if leaderboard:
        st.write("")
        st.subheader("🏆 Bảng Vàng Space Vocab Defender")
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        cols_lb = st.columns(min(5, len(leaderboard)))
        for idx, row in enumerate(leaderboard[:5]):
            with cols_lb[idx]:
                st.markdown(f"""
                <div class="kpi-card" style="text-align: center; padding: 14px;">
                    <div style="font-size: 1.4rem;">{medals[idx]}</div>
                    <div style="font-weight: 700; color: #0F172A; margin-top: 4px;">{row.get('username', '')}</div>
                    <div style="color: #4F46E5; font-weight: 800; font-size: 1.05rem;">{row.get('high_score', 0):,} đ</div>
                    <div style="font-size: 0.78rem; color: #64748B;">Max Combo x{row.get('max_combo', 0)}</div>
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# TRẠNG THÁI 2: CHƯA ĐĂNG NHẬP -> LANDING + LOGIN CARD
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
        <div class="hero-banner" style="margin-bottom: 1.2rem;">
            <div class="hero-title">📖 Vocabulary Trainer</div>
            <div class="hero-sub">Nền tảng học từ vựng tiếng Anh thông minh tích hợp AI & Game phản xạ tốc độ cao.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="feature-pill">
            <b>🤖 Trợ lý AI toàn diện:</b> Tự động dịch nghĩa, phân tích loại từ, tạo câu ví dụ và viết đoạn văn ngữ cảnh theo trình độ.
        </div>
        <div class="feature-pill">
            <b>🎬 Bóc từ qua YouTube:</b> Dán link video tiếng Anh bất kỳ để trích xuất phụ đề và lưu từ vựng chỉ với 1 cú click.
        </div>
        <div class="feature-pill">
            <b>🚀 Game bắn tàu vũ trụ:</b> Luyện phản xạ gõ từ vựng tiếng Anh siêu cuốn với hệ thống kỹ năng và bảng xếp hạng trực tuyến.
        </div>
        """, unsafe_allow_html=True)

    with col_auth:
        with st.container(border=True):
            tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])

            with tab_login:
                st.subheader("Chào mừng trở lại")
                login_user = st.text_input("Tên đăng nhập", key="login_user_input", placeholder="Nhập username của bạn")
                login_pass = st.text_input("Mật khẩu", type="password", key="login_pass_input", placeholder="Nhập mật khẩu")

                st.write("")
                if st.button("Đăng nhập ngay", use_container_width=True, type="primary"):
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
                st.subheader("Tạo tài khoản mới")
                reg_user = st.text_input("Tên đăng nhập mới", key="reg_user_input", placeholder="Ví dụ: thaihy2009")
                reg_pass = st.text_input("Mật khẩu mới", type="password", key="reg_pass_input")
                reg_pass_confirm = st.text_input("Xác nhận mật khẩu", type="password", key="reg_confirm_input")

                st.write("")
                if st.button("Tạo tài khoản", use_container_width=True, type="primary"):
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
