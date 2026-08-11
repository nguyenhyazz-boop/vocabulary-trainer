import json
import os
import bcrypt

USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(username, password):
    users = load_users()
    username = username.strip().lower()
    if username in users:
        return False, "Tên tài khoản đã tồn tại!"
    
    users[username] = {
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Đăng ký thành công!"

def login_user(username, password):
    users = load_users()
    username = username.strip().lower()
    if username not in users:
        return False, "Tài khoản không tồn tại!"
    
    if check_password(password, users[username]["password"]):
        return True, "Đăng nhập thành công!"
    return False, "Mật khẩu không chính xác!"
