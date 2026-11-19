import streamlit as st

def apply_global_theme(active_page: str = ""):
    st.markdown("""
    <style>
        /* 1. Ẩn thành phần thừa của Streamlit */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        [data-testid="stDeployButton"] { display: none !important; }
        header[data-testid="stHeader"] {
            background: rgba(250, 248, 242, 0.85);
            backdrop-filter: blur(8px);
        }

        /* 2. Sidebar tông kem ấm & chữ thuần tinh tế */
        [data-testid="stSidebar"] {
            background-color: #F6F3EB !important;
            border-right: 1px solid #E7E2D6 !important;
        }
        [data-testid="stSidebarNav"]::before {
            content: "VOCAB TRAINER";
            display: block;
            font-size: 0.95rem;
            font-weight: 800;
            letter-spacing: 1px;
            color: #1C1917;
            padding: 0.5rem 1.2rem 0.9rem 1.2rem;
            margin-bottom: 0.4rem;
            border-bottom: 1px solid #E7E2D6;
        }
        [data-testid="stSidebarNav"] li {
            margin-bottom: 2px !important;
        }
        [data-testid="stSidebarNav"] a {
            padding: 7px 14px !important;
            margin: 2px 10px !important;
            border-radius: 10px !important;
            transition: all 0.15s ease;
        }
        [data-testid="stSidebarNav"] a span {
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            color: #57534E !important;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: #EBE5D8 !important;
        }
        [data-testid="stSidebarNav"] a:hover span {
            color: #1C1917 !important;
        }

        /* Mục đang chọn */
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background-color: #FFFFFF !important;
            box-shadow: 0 2px 6px rgba(28, 25, 23, 0.05);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] span {
            color: #1C1917 !important;
            font-weight: 700 !important;
        }

        /* Đổi chữ "app" thành "Dashboard" ở mọi trạng thái */
        [data-testid="stSidebarNav"] ul li:first-child a span,
        [data-testid="stSidebarNavItems"] li:first-child a span {
            display: none !important;
        }
        [data-testid="stSidebarNav"] ul li:first-child a::after,
        [data-testid="stSidebarNavItems"] li:first-child a::after {
            content: "Dashboard";
            font-size: 0.9rem;
            font-weight: 500;
            color: #57534E;
        }
        [data-testid="stSidebarNav"] ul li:first-child a[aria-current="page"]::after,
        [data-testid="stSidebarNavItems"] li:first-child a[aria-current="page"]::after {
            color: #1C1917;
            font-weight: 700;
        }

        /* 3. Nút bấm & Input chuẩn phong cách Filko */
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

        /* 4. Tabs & Expander */
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

        /* 5. Mobile Responsive */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1.2rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.divider()
        if st.session_state.get("logged_in"):
            st.markdown(f"""
            <div style="background: #FFFFFF; border: 1px solid #E7E2D6; border-radius: 12px; padding: 12px 14px; margin-bottom: 8px;">
                <div style="font-size: 0.72rem; color: #78716C; font-weight: 700; letter-spacing: 0.5px;">ACCOUNT</div>
                <div style="font-size: 0.98rem; color: #1C1917; font-weight: 700; margin-top: 2px;">{st.session_state.get('username', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("Sign out", key=f"sidebar_logout_{active_page}", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.switch_page("app.py")
