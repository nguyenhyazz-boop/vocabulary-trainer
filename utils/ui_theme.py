import streamlit as st

def apply_global_theme(active_page: str = ""):
    st.markdown("""
    <style>
        /* 1. Brand Header ở đỉnh Sidebar */
[data-testid="stSidebarNav"]::before {
    content: "VOCAB TRAINER";
    display: block;
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    color: #4F46E5;
    padding: 0.6rem 1.2rem 0.8rem 1.2rem;
    margin-bottom: 0.4rem;
    border-bottom: 1px solid #F1F5F9;
}

/* 2. Thu gọn khoảng cách & tinh chỉnh font chữ thuần kiểu Linear/Notion */
[data-testid="stSidebarNav"] li {
    margin-bottom: 1px !important;
}
[data-testid="stSidebarNav"] a {
    padding: 7px 14px !important;
    margin: 2px 10px !important;
    border-radius: 8px !important;
    transition: all 0.15s ease;
}
[data-testid="stSidebarNav"] a span {
    font-size: 0.9rem !important;
    font-weight: 500 !important;
    color: #475569 !important;
}
[data-testid="stSidebarNav"] a:hover {
    background-color: #F1F5F9 !important;
}
[data-testid="stSidebarNav"] a:hover span {
    color: #0F172A !important;
}

/* Mục đang chọn: Nền xanh nhạt, chữ đậm sắc nét */
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background-color: #EEF2FF !important;
    border-left: none !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] span {
    color: #4F46E5 !important;
    font-weight: 700 !important;
}

/* Đổi chữ "app" thành "Dashboard" ở mọi trạng thái (active & hover) */
[data-testid="stSidebarNav"] ul li:first-child a span,
[data-testid="stSidebarNavItems"] li:first-child a span {
    display: none !important;
}
[data-testid="stSidebarNav"] ul li:first-child a::after,
[data-testid="stSidebarNavItems"] li:first-child a::after {
    content: "Dashboard";
    font-size: 0.9rem;
    font-weight: 600;
    color: #475569;
}
[data-testid="stSidebarNav"] ul li:first-child a[aria-current="page"]::after,
[data-testid="stSidebarNavItems"] li:first-child a[aria-current="page"]::after {
    color: #4F46E5;
    font-weight: 700;
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
