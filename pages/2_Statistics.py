import streamlit as st
import pandas as pd
from utils.data_manager import load_data

st.set_page_config(page_title="Statistics - Vocabulary Trainer", page_icon="📊", layout="wide")

st.title("📊 Thống kê học tập")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

colloc_file = f"data_collocation_{username}.json"
vocab_file = f"data_vocab_{username}.json"

colloc_data = load_data(colloc_file)
vocab_data = load_data(vocab_file)

# 1. PHÂN BỔ KHO TỪ VỰNG
st.subheader("📁 Phân bổ theo kho từ vựng")
col1, col2 = st.columns(2)

with col1:
    st.info(f"🔗 **Collocations** (`{colloc_file}`): **{len(colloc_data)}** từ")

with col2:
    st.success(f"🔤 **Normal Vocabulary** (`{vocab_file}`): **{len(vocab_data)}** từ")

st.divider()

# 2. TOP TỪ CẦN LUYỆN TẬP THÊM (SAI NHIỀU NHẤT)
st.subheader("⚠️ Top từ cần luyện tập thêm (Sai nhiều nhất)")

user_all_words = {**colloc_data, **vocab_data}

wrong_words = []
for word, item in user_all_words.items():
    if isinstance(item, dict):
        wrong_count = item.get("wrong", 0)
        correct_count = item.get("correct", 0)
        meaning = item.get("meaning", "")
        if wrong_count > 0:
            wrong_words.append({
                "Word": word,
                "Meaning": meaning,
                "Wrong": wrong_count,
                "Correct": correct_count
            })

if wrong_words:
    wrong_df = pd.DataFrame(wrong_words)
    wrong_df = wrong_df.sort_values(by="Wrong", ascending=False)
    st.dataframe(wrong_df, use_container_width=True)
else:
    st.success("🎉 Cực kỳ xuất sắc! Bạn chưa làm sai từ nào cả.")

st.divider()

# 3. BIỂU ĐỒ HOẠT ĐỘNG
st.subheader("📈 Tiến độ học tập")

chart_data = []
for word, item in user_all_words.items():
    if isinstance(item, dict):
        correct_count = item.get("correct", 0)
        wrong_count = item.get("wrong", 0)
        if correct_count > 0 or wrong_count > 0:
            chart_data.append({
                "Word": word,
                "Correct": correct_count,
                "Wrong": wrong_count
            })

if chart_data:
    df_chart = pd.DataFrame(chart_data).set_index("Word")
    st.bar_chart(df_chart)
else:
    st.info("Chưa có dữ liệu làm bài để hiển thị biểu đồ. Hãy sang trang **Study** hoặc **Quiz** làm bài nhé!")
