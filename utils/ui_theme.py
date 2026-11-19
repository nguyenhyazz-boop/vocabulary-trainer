import streamlit as st

def apply_global_theme(active_page: str = ""):
    st.markdown("""
    <style>
        /* 1. Ẩn thành phần thừa của Streamlit */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        [data-testid="stDeployButton"] { display: none !important; }
        [data-testid="stSidebarCollapseButton"] { display: none !important; }
        header[data-testid="stHeader"] {
            background: rgba(250, 248, 242, 0.85);
            backdrop-filter: blur(8px);
        }

        /* 2. Thu gọn Sidebar thành dải Icon Rail (~78px) giữ nguyên màu kem ấm hiện tại */
        [data-testid="stSidebar"] {
            min-width: 78px !important;
            max-width: 78px !important;
            width: 78px !important;
            background-color: #F6F3EB !important;
            border-right: 1px solid #E7E2D6 !important;
            overflow: visible !important;
        }
        [data-testid="stSidebar"] > div:first-child {
            width: 78px !important;
            overflow: visible !important;
            padding-top: 0.6rem !important;
        }

        /* Logo app vuông bo góc mềm mại ở đỉnh Rail (tông tím Lavender khớp theme hiện tại) */
        [data-testid="stSidebarNav"]::before {
            content: "";
            display: block;
            width: 44px;
            height: 44px;
            margin: 0 auto 14px auto;
            border-radius: 13px;
            background-color: #EDE9FE;
            border: 1px solid #DDD6FE;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%237C3AED' stroke-width='2.4' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: center;
            background-size: 22px 22px;
        }

        /* Ẩn chữ mặc định của menu */
        [data-testid="stSidebarNav"] ul,
        [data-testid="stSidebarNavItems"] {
            padding: 0 !important;
            overflow: visible !important;
        }
        [data-testid="stSidebarNav"] li {
            margin: 2px 0 !important;
            position: relative !important;
            overflow: visible !important;
        }
        [data-testid="stSidebarNav"] a span {
            display: none !important;
        }

        /* Nút icon từng trang */
        [data-testid="stSidebarNav"] a {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            width: 100% !important;
            height: 46px !important;
            padding: 0 !important;
            margin: 0 !important;
            border-radius: 0 !important;
            position: relative !important;
            transition: all 0.18s ease !important;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: rgba(124, 58, 237, 0.05) !important;
        }

        /* Hiệu ứng Active giống ảnh mẫu: Vạch dọc bên trái + dải glow loang nhẹ */
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, rgba(124, 58, 237, 0.14) 0%, rgba(124, 58, 237, 0.03) 75%, transparent 100%) !important;
        }
        [data-testid="stSidebarNav"] a[aria-current="page"]::before {
            content: "";
            position: absolute;
            left: 0;
            top: 4px;
            bottom: 4px;
            width: 3.5px;
            background-color: #7C3AED;
            border-radius: 0 4px 4px 0;
        }

        /* Khung chứa Icon SVG nét mảnh */
        [data-testid="stSidebarNav"] a::after {
            content: "";
            width: 21px;
            height: 21px;
            display: block;
            background-repeat: no-repeat;
            background-position: center;
            background-size: contain;
            opacity: 0.55;
            transition: opacity 0.18s ease, transform 0.18s ease;
        }
        [data-testid="stSidebarNav"] a:hover::after {
            opacity: 0.9;
            transform: scale(1.06);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"]::after {
            opacity: 1;
        }

        /* --- BỘ 11 ICON SVG VECTOR ĐỒNG BỘ THEO THỨ TỰ TRANG --- */
        /* 1. Dashboard */
        [data-testid="stSidebarNav"] li:nth-child(1) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'/%3E%3Cpolyline points='9 22 9 12 15 12 15 22'/%3E%3C/svg%3E");
        }
        /* 2. Study */
        [data-testid="stSidebarNav"] li:nth-child(2) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z'/%3E%3Cpath d='M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z'/%3E%3C/svg%3E");
        }
        /* 3. Statistics */
        [data-testid="stSidebarNav"] li:nth-child(3) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3Cpath d='M8 16v-5'/%3E%3Cpath d='M12 16V8'/%3E%3Cpath d='M16 16v-3'/%3E%3C/svg%3E");
        }
        /* 4. Wrong Words */
        [data-testid="stSidebarNav"] li:nth-child(4) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cline x1='12' y1='8' x2='12' y2='12'/%3E%3Cline x1='12' y1='16' x2='12.01' y2='16'/%3E%3C/svg%3E");
        }
        /* 5. Add Word */
        [data-testid="stSidebarNav"] li:nth-child(5) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Cline x1='12' y1='8' x2='12' y2='16'/%3E%3Cline x1='8' y1='12' x2='16' y2='12'/%3E%3C/svg%3E");
        }
        /* 6. Quiz */
        [data-testid="stSidebarNav"] li:nth-child(6) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='12' cy='12' r='10'/%3E%3Ccircle cx='12' cy='12' r='6'/%3E%3Ccircle cx='12' cy='12' r='2'/%3E%3C/svg%3E");
        }
        /* 7. Search */
        [data-testid="stSidebarNav"] li:nth-child(7) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='8'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E");
        }
        /* 8. Library */
        [data-testid="stSidebarNav"] li:nth-child(8) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m16 6 4 14'/%3E%3Cpath d='M12 6v14'/%3E%3Cpath d='M8 8v12'/%3E%3Cpath d='M4 4v16'/%3E%3C/svg%3E");
        }
        /* 9. AI Reader */
        [data-testid="stSidebarNav"] li:nth-child(9) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z'/%3E%3C/svg%3E");
        }
        /* 10. Space Shooter */
        [data-testid="stSidebarNav"] li:nth-child(10) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z'/%3E%3Cpath d='m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z'/%3E%3C/svg%3E");
        }
        /* 11. Video Vocab */
        [data-testid="stSidebarNav"] li:nth-child(11) a::after {
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%231C1917' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='2' y='4' width='20' height='16' rx='3'/%3E%3Cpolygon points='10 9 15 12 10 15 10 9'/%3E%3C/svg%3E");
        }

        /* Tooltip hiện tên trang khi rê chuột vào icon */
        [data-testid="stSidebarNav"] li:hover::after {
            position: absolute;
            left: 84px;
            top: 50%;
            transform: translateY(-50%);
            background-color: #18181B;
            color: #FAF8F2;
            padding: 5px 11px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            white-space: nowrap;
            z-index: 99999;
            box-shadow: 0 4px 12px rgba(24, 24, 27, 0.18);
            pointer-events: none;
        }
        [data-testid="stSidebarNav"] li:nth-child(1):hover::after { content: "Dashboard"; }
        [data-testid="stSidebarNav"] li:nth-child(2):hover::after { content: "Study Flashcards"; }
        [data-testid="stSidebarNav"] li:nth-child(3):hover::after { content: "Statistics"; }
        [data-testid="stSidebarNav"] li:nth-child(4):hover::after { content: "Wrong Words"; }
        [data-testid="stSidebarNav"] li:nth-child(5):hover::after { content: "Add Word"; }
        [data-testid="stSidebarNav"] li:nth-child(6):hover::after { content: "Quiz"; }
        [data-testid="stSidebarNav"] li:nth-child(7):hover::after { content: "Search"; }
        [data-testid="stSidebarNav"] li:nth-child(8):hover::after { content: "Library"; }
        [data-testid="stSidebarNav"] li:nth-child(9):hover::after { content: "AI Reader"; }
        [data-testid="stSidebarNav"] li:nth-child(10):hover::after { content: "Space Shooter"; }
        [data-testid="stSidebarNav"] li:nth-child(11):hover::after { content: "Video Vocab"; }

        /* 3. Giữ nguyên giao diện Nút bấm, Input, Tabs chuẩn Editorial */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.1rem !important;
            transition: all 0.15s ease !important;
        }
        .stButton > button[kind="primary"] {
            background-color: #18181B !important;
            color: #FAF8F2 !important;
            border: none !important;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #27272A !important;
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(24, 24, 27, 0.18);
        }
        [data-baseweb="input"], [data-baseweb="select"] > div, textarea {
            background-color: #FFFFFF !important;
            border-radius: 10px !important;
            border-color: #DCD6C8 !important;
        }
        [data-baseweb="input"]:focus-within, textarea:focus {
            border-color: #18181B !important;
            box-shadow: 0 0 0 2px rgba(24, 24, 27, 0.1) !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            background-color: #EFECE3;
            padding: 5px;
            border-radius: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            font-weight: 600 !important;
            color: #57534E !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #1C1917 !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.05);
        }
        [data-testid="stExpander"] {
            background-color: #FFFFFF;
            border: 1px solid #E7E2D6 !important;
            border-radius: 14px !important;
        }
        @media (max-width: 768px) {
            [data-testid="stSidebar"] {
                min-width: 64px !important;
                max-width: 64px !important;
                width: 64px !important;
            }
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1.2rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Nút đăng xuất nhỏ gọn bằng icon ở đáy thanh Icon Rail
    with st.sidebar:
        st.divider()
        if st.session_state.get("logged_in"):
            if st.button("⎋", key=f"sidebar_logout_{active_page}", help=f"Sign out ({st.session_state.get('username', '')})", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.switch_page("app.py")
