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

def parse_file_info(file_name: str):
    """
    Tách tên file (vd: data_vocab_admin.json) thành username và data_type
    """
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
    """
    Đọc dữ liệu từ Supabase Database
    """
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
    """
    Lưu dữ liệu trực tiếp vào Supabase Database
    """
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
        
        # Upsert: Nếu đã có record của user đó thì cập nhật, chưa có thì thêm mới
        supabase.table("user_data").upsert(
            payload, 
            on_conflict="username, data_type"
        ).execute()
        return True
    except Exception as e:
        st.error(f"Lỗi lưu dữ liệu vào Database: {e}")
        return False
