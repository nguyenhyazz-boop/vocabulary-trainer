import streamlit as st
import json
import random

st.title("❌ Review Wrong Words")


# --- 1. HÀM ĐỌC & LƯU DATA.JSON ---
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()

# --- 2. LỌC DANH SÁCH CÁC TỪ BỊ SAI ---
# Lấy những từ mà số lần 'wrong' > 0
wrong_words_list = []
for word, info in data.items():
    if isinstance(info, dict) and info.get("wrong", 0) > 0:
        wrong_words_list.append(word)

if not wrong_words_list:
    st.success("🎉 Tuyệt vời! Bạn không có từ nào trong danh sách bị sai cả.")
    st.stop()

# --- 3. KHỞI TẠO TRẠNG THÁI KHÔNG LẶP TỪ BỊ SAI ---
if "wrong_studied" not in st.session_state:
    st.session_state.wrong_studied = []

remaining_wrong = [w for w in wrong_words_list if w not in st.session_state.wrong_studied]

# Nếu đã ôn hết danh sách từ sai trong phiên
if not remaining_wrong:
    st.balloons()
    st.success("🎉 Bạn đã hoàn thành ôn tập lại toàn bộ danh sách từ sai!")
    if st.button("Ôn lại từ sai lần nữa"):
        st.session_state.wrong_studied = []
        st.rerun()
    st.stop()

# Chọn từ sai ngẫu nhiên
if "current_wrong_word" not in st.session_state or st.session_state.current_wrong_word in st.session_state.wrong_studied:
    st.session_state.current_wrong_word = random.choice(remaining_wrong)

current_word = st.session_state.current_wrong_word

# --- 4. PROGRESS BAR THỐNG KÊ ---
total_wrong_count = len(wrong_words_list)
studied_count = len(st.session_state.wrong_studied)
progress = studied_count / total_wrong_count if total_wrong_count > 0 else 0

if len(wrong_words) == 0:
    st.success("🎉 Bạn đã hoàn thành xuất sắc tất cả các từ sai!")
    st.balloons()
else:
    progress_value = min(max(float(progress), 0.0), 1.0)
    st.progress(progress_value)
st.write(f"Đã ôn tập: **{studied_count} / {total_wrong_count}** từ sai")

# --- 5. HIỂN THỊ TỪ VỰNG & SHOW MEANING ---
st.divider()
st.subheader(f"Word: {current_word}")

# Hiển thị số lần sai thực tế của từ này
wrong_count = data[current_word].get("wrong", 0)
correct_count = data[current_word].get("correct", 0)
st.caption(f"📊 Thống kê từ này: **{correct_count}** đúng / **{wrong_count}** sai")

# Show Meaning (tự đóng khi chuyển từ nhờ key động)
with st.expander("👀 Show Meaning", expanded=False, key=f"expander_wrong_{current_word}"):
    word_info = data[current_word]
    if isinstance(word_info, dict):
        meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    else:
        meaning = str(word_info)
    st.write(meaning)

# --- 6. NÚT XỬ LÝ CORRECT / WRONG ---
st.write("---")
col1, col2 = st.columns(2)


def handle_wrong_answer(is_correct):
    st.session_state.wrong_studied.append(current_word)

    if isinstance(data[current_word], dict):
        if is_correct:
            data[current_word]["correct"] += 1
            # Nếu trả lời đúng, trừ bớt 1 lần sai để khuyến khích
            if data[current_word]["wrong"] > 0:
                data[current_word]["wrong"] -= 1
        else:
            data[current_word]["wrong"] += 1

    save_data(data)


with col1:
    if st.button("✅ Correct", use_container_width=True):
        handle_wrong_answer(True)
        st.rerun()

with col2:
    if st.button("❌ Wrong", use_container_width=True):
        handle_wrong_answer(False)
        st.rerun()
