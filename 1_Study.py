import streamlit as st
import json
import random

st.title("📖 Study Vocabulary")


# --- 1. HÀM ĐỌC & LƯU FILE DATA.JSON ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()
all_words = list(data.keys())

# --- 2. KHỞI TẠO TRẠNG THÁI KHÔNG LẶP TỪ ---
if "studied_words" not in st.session_state:
    st.session_state.studied_words = []

# Lọc ra các từ chưa học trong phiên hiện tại
remaining_words = [w for w in all_words if w not in st.session_state.studied_words]

# Khi đã học hết tất cả các từ trong file
if not remaining_words:
    st.success("🎉 Bạn đã học hết tất cả các từ trong phiên này!")
    if st.button("Học lại từ đầu"):
        st.session_state.studied_words = []
        st.rerun()
    st.stop()

# Chọn từ mới nếu chưa có từ hiện tại hoặc từ hiện tại vừa được bấm trả lời
if "current_word" not in st.session_state or st.session_state.current_word in st.session_state.studied_words:
    st.session_state.current_word = random.choice(remaining_words)

current_word = st.session_state.current_word

# --- 3. PROGRESS BAR & SỐ TỪ ĐÃ HỌC ---
total_words = len(all_words)
studied_count = len(st.session_state.studied_words)

progress = studied_count / total_words if total_words > 0 else 0
st.progress(progress)
st.write(f"Số từ đã học trong phiên: **{studied_count} / {total_words}** từ")

# --- 4. HIỂN THỊ TỪ VỰNG & SHOW MEANING ---
st.divider()
st.subheader(f"Word: {current_word}")

# Sử dụng key động theo tên từ vựng để ép Streamlit reset expander về trạng thái đóng khi đổi từ
with st.expander("👀 Show Meaning", expanded=False, key=f"expander_{current_word}"):
    word_info = data[current_word]
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    else:
        meaning = str(word_info)
    st.write(meaning)

# --- 5. NÚT CORRECT / WRONG & TỰ LƯU DATA.JSON ---
st.write("---")
col1, col2 = st.columns(2)


def handle_answer(is_correct):
    # Đánh dấu từ đã học
    st.session_state.studied_words.append(current_word)

    # Cập nhật số lần đúng/sai vào data.json
    if isinstance(data[current_word], dict):
        if "correct" not in data[current_word]:
            data[current_word]["correct"] = 0
        if "wrong" not in data[current_word]:
            data[current_word]["wrong"] = 0

        if is_correct:
            data[current_word]["correct"] += 1
        else:
            data[current_word]["wrong"] += 1

    save_data(data)


with col1:
    if st.button("✅ Correct", use_container_width=True):
        handle_answer(True)
        st.rerun()

with col2:
    if st.button("❌ Wrong", use_container_width=True):
        handle_answer(False)
        st.rerun()