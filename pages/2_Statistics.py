import streamlit as st
from utils.data_manager import load_data

st.set_page_config(page_title="Statistics - Vocabulary Trainer", page_icon="📊", layout="wide")

st.title("📊 Thống kê tiến độ học tập")

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ (App) trước để xem thống kê cá nhân!")
    st.stop()

username = st.session_state.username
st.caption(f"Dữ liệu thống kê cho tài khoản: **{username}**")

# Đọc 2 kho dữ liệu riêng của User
colloc_file = f"data_collocation_{username}.json"
vocab_file = f"data_vocab_{username}.json"

colloc_data = load_data(colloc_file)
vocab_data = load_data(vocab_file)

# Gộp dữ liệu để tính tổng
all_data = {**colloc_data, **vocab_data}

if not all_data:
    st.info("💡 Bạn chưa có từ vựng nào trong cả 2 kho. Hãy sang trang 'Add Word' để thêm từ mới!")
    st.stop()

# --- TÍNH TOÁN THỐNG KÊ ---
total_words = len(all_data)
total_correct = sum(item.get("correct", 0) for item in all_data.values() if isinstance(item, dict))
total_wrong = sum(item.get("wrong", 0) for item in all_data.values() if isinstance(item, dict))
total_attempts = total_correct + total_wrong

accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0

# --- HIỂN THỊ METRICS ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("📖 Tổng số từ", f"{total_words} từ")
col2.metric("✅ Trả lời đúng", f"{total_correct} lần")
col3.metric("❌ Trả lời sai", f"{total_wrong} lần")
col4.metric("🎯 Độ chính xác", f"{accuracy:.1f}%")

st.divider()

# --- CHI TIẾT THEO TỪNG KHO ---
st.subheader("📁 Phân bổ theo kho từ vựng")
c1, c2 = st.columns(2)

with c1:
    st.info(f"🔗 **Collocations (`data_collocation_{username}.json`):** {len(colloc_data)} từ")

with c2:
    st.success(f"🔤 **Normal Vocabulary (`data_vocab_{username}.json`):** {len(vocab_data)} từ")

st.divider()

# --- TOP TỪ BỊ SAI NHIỀU NHẤT ---
st.subheader("⚠️ Top từ cần luyện tập thêm (Sai nhiều nhất)")

# Lọc các từ có số lần sai > 0 và sắp xếp giảm dần
wrong_words = [
    (word, item.get("wrong", 0), item.get("meaning", "")) 
    for word, item in all_data.items() 
    if isinstance(item, dict) and item.get("wrong", 0) > 0
]

wrong_words.sort(key=lambda x: x[1], reverse=True)

if wrong_words:
    for word, wrong_count, meaning in wrong_words[:5]:
        st.write(f"🔴 **{word}** — *{meaning}* (Sai: **{wrong_count}** lần)")
else:
    st.success("🎉 Cực kỳ xuất sắc! Bạn chưa làm sai từ nào cả.")

df = pd.DataFrame(chart_data).set_index("Date")

# Vẽ biểu đồ cột chồng (Stacked Bar Chart)
st.bar_chart(df, color=["#28a745", "#dc3545"])
