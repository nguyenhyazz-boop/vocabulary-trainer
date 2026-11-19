import streamlit as st

def apply_global_theme(active_page: str = ""):
    st.markdown("""
    <style>
        /* 1. Ẩn thanh công cụ thừa của Streamlit (Deploy, Menu 3 chấm, Footer) */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        [data-testid="stDeployButton"] { display: none !important; }
        header[data-testid="stHeader"] {
            background: rgba(248, 250, 252, 0.85);
            backdrop-filter: blur(8px);
        }

        /* 2. Tùy chỉnh thanh Sidebar hiện đại */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        [data-testid="stSidebarNav"] {
            padding-top: 0.75rem;
        }
        [data-testid="stSidebarNav"] span {
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            color: #334155;
        }
        [data-testid="stSidebarNav"] a {
            border-radius: 10px !important;
            margin: 3px 10px !important;
            padding: 8px 12px !important;
            transition: all 0.15s ease;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: #EEF2FF !important;
            color: #4F46E5 !important;
            transform: translateX(3px);
        }
        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(90deg, #EEF2FF 0%, #E0E7FF 100%) !important;
            color: #4F46E5 !important;
            border-left: 3px solid #4F46E5;
        }

        /* 3. Bo góc mềm mại & nâng cấp Input, Selectbox, Button */
        .stButton > button {
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.5rem 1rem !important;
            transition: all 0.15s ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.15);
        }
        [data-baseweb="input"], [data-baseweb="select"] > div, textarea {
            border-radius: 10px !important;
            border-color: #CBD5E1 !important;
        }
        [data-baseweb="input"]:focus-within, textarea:focus {
            border-color: #4F46E5 !important;
            box-shadow: 0 0 0 2px rgba(79, 70, 229, 0.15) !important;
        }

        /* 4. Làm đẹp Tabs & Expander */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #F1F5F9;
            padding: 5px;
            border-radius: 12px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px !important;
            font-weight: 600 !important;
            padding: 6px 16px !important;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF !important;
            color: #4F46E5 !important;
            box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06);
        }
        [data-testid="stExpander"] {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
        }

        /* 5. Tối ưu giao diện trên điện thoại (Mobile Responsive) */
        @media (max-width: 768px) {
            .main .block-container {
                padding-left: 1rem !important;
                padding-right: 1rem !important;
                padding-top: 1.2rem !important;
            }
            h1, .app-title {
                font-size: 1.45rem !important;
            }
        }
    </style>
    """, unsafe_allow_html=True)

    # Hiển thị thẻ thông tin tài khoản ở đáy Sidebar
    with st.sidebar:
        st.divider()
        if st.session_state.get("logged_in"):
            st.markdown(f"""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 12px; padding: 12px; margin-bottom: 8px;">
                <div style="font-size: 0.75rem; color: #64748B; font-weight: 600;">PHI CÔNG ĐANG ĐĂNG NHẬP</div>
                <div style="font-size: 1rem; color: #0F172A; font-weight: 700; margin-top: 2px;">👤 {st.session_state.get('username', '')}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚪 Đăng xuất", key=f"sidebar_logout_{active_page}", use_container_width=True):
                st.session_state.logged_in = False
                st.session_state.username = ""
                st.switch_page("app.py")
