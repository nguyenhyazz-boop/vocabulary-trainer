import base64
import streamlit as st
from utils.data_manager import load_data, save_data, register_user, authenticate_user

st.set_page_config(page_title="Vocabulary Trainer", page_icon="📖", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 680px !important;
    }
    
    [data-testid="stSidebarNav"] span {
        font-size: 1.15rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebarNav"] a {
        padding: 8px 12px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("📖 Vocabulary Trainer")
st.caption("Ứng dụng quản lý và luyện tập từ vựng tiếng Anh cá nhân hóa.")

# Quản lý trạng thái đăng nhập
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    st.success(f"Xin chào **{st.session_state.username}**! Bạn đã đăng nhập thành công.")
    if st.button("Đăng xuất", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
else:
    tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])

    # --- TAB ĐĂNG NHẬP ---
    with tab_login:
        st.subheader("Đăng nhập")
        login_user = st.text_input("Tên đăng nhập", key="login_user_input")
        login_pass = st.text_input("Mật khẩu", type="password", key="login_pass_input")

        if st.button("Đăng nhập", use_container_width=True, type="primary"):
            if not login_user or not login_pass:
                st.warning("Vui lòng nhập đầy đủ thông tin!")
            else:
                if authenticate_user(login_user, login_pass):
                    st.session_state.logged_in = True
                    st.session_state.username = login_user
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")

    # --- TAB ĐĂNG KÝ ---
    with tab_register:
        st.subheader("Đăng ký tài khoản mới")
        reg_user = st.text_input("Tên đăng nhập mới", key="reg_user_input")
        reg_pass = st.text_input("Mật khẩu mới", type="password", key="reg_pass_input")
        reg_pass_confirm = st.text_input("Xác nhận mật khẩu", type="password", key="reg_confirm_input")

        if st.button("Đăng ký", use_container_width=True):
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
