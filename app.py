import base64
import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Vocabulary Trainer - Home", page_icon="📖", layout="wide")

# Khởi tạo trạng thái đăng nhập trong Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Đọc danh sách tài khoản người dùng
users_data = load_data("users.json")

# --- HIỂN THỊ KHI ĐÃ ĐĂNG NHẬP ---
if st.session_state.logged_in:
    username = st.session_state.username
    st.title(f"👋 Chào mừng quay trở lại, {username}!")

    # Đọc cấu hình thông tin cá nhân của User (bao gồm Avatar)
    user_config_file = f"user_profile_{username}.json"
    user_profile = load_data(user_config_file)
    current_avatar = user_profile.get("avatar", None)

    # Hiển thị thông tin người dùng ở Thanh Menu bên trái (Sidebar)
    with st.sidebar:
        if current_avatar:
            st.image(current_avatar, width=100)
        else:
            st.markdown("### 👤 Chưa có Avatar")
        st.markdown(f"**Tài khoản:** `{username}`")
        st.divider()
        if st.button("🚪 Đăng xuất", type="secondary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    # SECTION: CÀI ĐẶT AVATAR CÁ NHÂN
    st.write("---")
    st.subheader("🖼️ Cài đặt Ảnh đại diện (Avatar)")
    
    col_avt1, col_avt2 = st.columns([1, 2])
    
    with col_avt1:
        if current_avatar:
            st.image(current_avatar, width=150, caption=f"Avatar của {username}")
        else:
            st.info("Bạn chưa thiết lập ảnh đại diện.")

    with col_avt2:
        uploaded_file = st.file_uploader(
            "Tải ảnh từ máy tính của bạn (PNG, JPG, JPEG):", 
            type=["png", "jpg", "jpeg"],
            key="avatar_uploader"
        )
        
        if uploaded_file is not None:
            # Mã hóa ảnh sang chuỗi Base64
            bytes_data = uploaded_file.getvalue()
            base64_image = f"data:image/png;base64,{base64.b64encode(bytes_data).decode()}"
            
            if st.button("💾 Lưu ảnh đại diện này", type="primary", use_container_width=True):
                user_profile["avatar"] = base64_image
                save_data(user_profile, user_config_file)
                st.success("🎉 Đã cập nhật Avatar thành công!")
                st.rerun()

    st.write("---")
    st.info("💡 Hãy chọn các tính năng trên thanh menu bên trái (**Library, Study, Quiz, Statistics...**) để bắt đầu học tập nhé!")

# --- HIỂN THỊ KHI CHƯA ĐĂNG NHẬP (GIAO DIỆN LOGIN / REGISTER) ---
else:
    st.title("📖 Vocabulary Trainer")
    st.caption("Ứng dụng quản lý và luyện tập từ vựng tiếng Anh cá nhân hóa.")

    tab_login, tab_register = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])

    # TAB 1: ĐĂNG NHẬP
   # Logic Đăng nhập:
if authenticate_user(login_username, login_password):
    st.session_state.logged_in = True
    st.session_state.username = login_username
    st.success("Đăng nhập thành công!")
    st.rerun()
else:
    st.error("Tên đăng nhập hoặc mật khẩu không chính xác!")
    # TAB 2: ĐĂNG KÝ
 from utils.data_manager import register_user, authenticate_user

# Logic Đăng ký:
success, msg = register_user(reg_username, reg_password)
if success:
    st.success(msg)
else:
    st.error(msg)
                
                # Tạo sẵn 2 file dữ liệu trống cho tài khoản mới
                save_data({}, f"data_collocation_{reg_user}.json")
                save_data({}, f"data_vocab_{reg_user}.json")
                save_data({}, f"user_profile_{reg_user}.json")
                
                st.success("🎉 Đăng ký tài khoản thành công! Vui lòng chuyển sang Tab 'Đăng nhập'.")
