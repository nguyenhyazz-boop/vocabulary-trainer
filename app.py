import streamlit as st
from utils.data_manager import load_data

# =========================
# Cấu hình trang
# =========================
st.set_page_config(
    page_title="Vocabulary Trainer",
    page_icon="🌿",
    layout="wide"
)

# Custom CSS cho phong cách Chill / Minimalist
st.markdown("""
    <style>
    /* Nền ứng dụng màu kem dịu mắt */
    .stApp {
        background-color: #FAF8F5;
    }
    
    /* Khung Metric bo góc, có bóng nhẹ */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.04);
        border: 1px solid #EAE6DF;
    }
    
    /* Chỉnh kiểu chữ cho Tiêu đề */
    .main-title {
        font-size: 2.3rem;
        font-weight: 700;
        color: #2D3142;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #6C757D;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# Đọc dữ liệu
# =========================
data = load_data()

# =========================
# Thống kê (Giữ nguyên logic, thêm .get để tránh lỗi KeyError)
# =========================
total_words = len(data)

total_correct = sum(item.get("correct", 0) for item in data.values())
total_wrong = sum(item.get("wrong", 0) for item in data.values())

accuracy = (
    total_correct / (total_correct + total_wrong) * 100
    if (total_correct + total_wrong) > 0
    else 0
)

# =========================
# Giao diện
# =========================
st.markdown('<div class="main-title">🌿 Vocabulary Trainer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Welcome to Version 1.0 of my vocabulary learning application!</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📖 Total Words", total_words)

with col2:
    st.metric("✅ Correct", total_correct)

with col3:
    st.metric("🎯 Accuracy", f"{accuracy:.1f}%")

st.divider()

st.success("🚀 Version 1.0 is under development.")
st.write("TEST")
