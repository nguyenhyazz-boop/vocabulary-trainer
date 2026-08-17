import streamlit as st
from supabase import create_client, Client

# Khởi tạo kết nối Supabase
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets.get("SUPABASE_URL", "").strip()
    key = st.secrets.get("SUPABASE_KEY", "").strip()
    if not url or not key:
        return None
    return create_client(url, key)

# --- QUẢN LÝ TÀI KHOẢN (USERS) ---
def register_user(username, password):
    supabase = get_supabase_client()
    if not supabase:
        st.error("Chưa cấu hình Supabase Key trong Secrets!")
        return False, "Lỗi cấu hình database."
    
    try:
        # Kiểm tra xem username đã tồn tại chưa
        check = supabase.table("users").select("username").eq("username", username).execute()
        if check.data and len(check.data) > 0:
            return False, "Tên tài khoản đã tồn tại!"
        
        # Thêm user mới
        supabase.table("users").insert({"username": username, "password": password}).execute()
        return True, "Đăng ký thành công!"
    except Exception as e:
        return False, f"Lỗi đăng ký: {e}"

def authenticate_user(username, password):
    supabase = get_supabase_client()
    if not supabase:
        return False
    
    try:
        response = supabase.table("users").select("*").eq("username", username).eq("password", password).execute()
        if response.data and len(response.data) > 0:
            return True
        return False
    except Exception as e:
        st.error(f"Lỗi xác thực: {e}")
        return False

# --- QUẢN LÝ DỮ LIỆU TỪ VỰNG & LỊCH SỬ ---
def parse_file_info(file_name: str):
    clean_name = file_name.replace(".json", "")
    parts = clean_name.split("_")
    
    if "ai_history" in clean_name:
        data_type = "ai_history"
        username = parts[-1] if len(parts) > 2 else "default"
    elif "collocation" in clean_name:
        data_type = "collocation"
        username = parts[-1] if len(parts) > 2 else "default"
    elif "vocab" in clean_name:
        data_type = "vocab"
        username = parts[-1] if len(parts) > 2 else "default"
    else:
        data_type = "other"
        username = "default"
        
    return username, data_type

def load_data(file_name: str):
    supabase = get_supabase_client()
    if not supabase:
        return {} if "history" not in file_name else []

    username, data_type = parse_file_info(file_name)

    try:
        response = supabase.table("user_data") \
            .select("content") \
            .eq("username", username) \
            .eq("data_type", data_type) \
            .execute()

        if response.data and len(response.data) > 0:
            return response.data[0]["content"]
        else:
            return [] if data_type == "ai_history" else {}
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu Database: {e}")
        return [] if data_type == "ai_history" else {}

def save_data(data, file_name: str):
    supabase = get_supabase_client()
    if not supabase:
        st.error("Chưa cấu hình Supabase Keys trong Streamlit Secrets!")
        return False

    username, data_type = parse_file_info(file_name)

    try:
        payload = {
            "username": username,
            "data_type": data_type,
            "content": data
        }
        
        supabase.table("user_data").upsert(
            payload, 
            on_conflict="username, data_type"
        ).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi lưu dữ liệu vào Database: {e}")
        return False
