import streamlit as st
from utils.data_manager import load_data

# =========================
# Cấu hình trang
# =========================
st.set_page_config(
    page_title="Vocabulary Trainer",
    page_icon="📚",
    layout="wide"
)

# =========================
# Đọc dữ liệu
# =========================
data = load_data()

# =========================
# Thống kê
# =========================
total_words = len(data)

total_correct = sum(item["correct"] for item in data.values())
total_wrong = sum(item["wrong"] for item in data.values())

accuracy = (
    total_correct / (total_correct + total_wrong) * 100
    if (total_correct + total_wrong) > 0
    else 0
)

# =========================
# Giao diện
# =========================
st.title("📚 Vocabulary Trainer")

st.write(
    "Welcome to Version 1.0 of my vocabulary learning application!"
)

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