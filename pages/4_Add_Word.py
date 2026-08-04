import streamlit as st
import json

st.title("➕ Add New Word")


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

# --- 2. FORM THÊM TỪ MỚI ---
with st.form("add_word_form", clear_on_submit=True):
    new_word = st.text_input("Từ vựng / Collocation mới:").strip()
    new_meaning = st.text_input("Nghĩa tiếng Việt:").strip()

    submitted = st.form_submit_button("➕ Thêm vào dữ liệu", type="primary")

    if submitted:
        if not new_word or not new_meaning:
            st.error("⚠️ Vui lòng nhập đầy đủ cả từ vựng và nghĩa!")
        else:
            # Chuyển từ về dạng chữ thường để tránh trùng lặp
            word_key = new_word.lower()

            if word_key in data:
                st.warning(f"⚠️ Từ **'{new_word}'** đã tồn tại trong data.json rồi!")
            else:
                # Tạo cấu trúc lưu trữ chuẩn cho từ mới
                data[word_key] = {
                    "meaning": new_meaning,
                    "correct": 0,
                    "wrong": 0
                }
                save_data(data)
                st.success(f"🎉 Đã thêm thành công từ: **{word_key}** - *{new_meaning}*")

st.divider()

# --- 3. HIỂN THỊ DẠNG DANH SÁCH BÊN DƯỚI DỄ QUẢN LÝ ---
st.subheader(f"📚 Danh sách từ vựng hiện có ({len(data)} từ)")

# Bảng xem nhanh các từ trong data.json
with st.expander("👀 Xem toàn bộ từ vựng"):
    for word, info in data.items():
        if isinstance(info, dict):
            m = info.get("meaning", info.get("definition", str(info)))
        else:
            m = str(info)
        st.write(f"- **{word}**: {m}")