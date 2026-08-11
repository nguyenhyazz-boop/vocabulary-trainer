import streamlit as st
from utils.auth_manager import login_user, register_user
from utils.data_manager import load_data

st.set_page_config(page_title="Vocabulary Trainer", page_icon="🌿", layout="wide")

# Khởi tạo session state cho user
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.title("🌱 Vocabulary Trainer")

# --- KHI CHƯA ĐĂNG NHẬP ---
if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký"])

    with tab1:
        st.subheader("Đăng nhập tài khoản")
        user_input = st.text_input("Tên đăng nhập:", key="login_user").strip().lower()
        pass_input = st.text_input("Mật khẩu:", type="password", key="login_pass")
        
        if st.button("Đăng nhập", type="primary", use_container_width=True):
            if user_input and pass_input:
                success, msg = login_user(user_input, pass_input)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = user_input
                    st.success(f"Chào mừng {user_input} quay trở lại!")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")
            else:
                st.warning("Vui lòng điền đầy đủ thông tin!")

    with tab2:
        st.subheader("Tạo tài khoản mới")
        reg_user = st.text_input("Tên đăng nhập:", key="reg_user").strip().lower()
        reg_pass = st.text_input("Mật khẩu:", type="password", key="reg_pass")
        reg_pass_confirm = st.text_input("Xác nhận mật khẩu:", type="password", key="reg_pass_confirm")

        if st.button("Đăng ký", use_container_width=True):
            if not reg_user or not reg_pass:
                st.warning("Vui lòng điền đầy đủ thông tin!")
            elif reg_pass != reg_pass_confirm:
                st.error("❌ Mật khẩu xác nhận không trùng khớp!")
            else:
                success, msg = register_user(reg_user, reg_pass)
                if success:
                    st.success("🎉 Đăng ký thành công! Hãy chuyển sang tab Đăng nhập.")
                else:
                    st.error(f"❌ {msg}")

    st.stop()

# --- KHI ĐÃ ĐĂNG NHẬP THÀNH CÔNG ---
st.sidebar.markdown(f"👤 Tài khoản: **{st.session_state.username}**")
if st.sidebar.button("🚪 Đăng xuất"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# Đọc thống kê kho từ vựng riêng của User
colloc_file = f"data_collocation_{st.session_state.username}.json"
vocab_file = f"data_vocab_{st.session_state.username}.json"

colloc_data = load_data(colloc_file)
vocab_data = load_data(vocab_file)

total_words = len(colloc_data) + len(vocab_data)

st.markdown(f"### 👋 Xin chào, **{st.session_state.username}**!")
st.caption("Góc nhỏ luyện tập từ vựng & collocations mỗi ngày.")

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("🔗 Collocations", f"{len(colloc_data)} từ")
col2.metric("🔤 Normal Vocab", f"{len(vocab_data)} từ")
col3.metric("📖 Tổng từ vựng", f"{total_words} từ")

st.divider()
st.info("👈 Chọn một chức năng bên thanh menu bên trái để bắt đầu học!")
