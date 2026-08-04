import streamlit as st
import json

st.title("🔍 Search Vocabulary")


# --- 1. HÀM ĐỌC DATA.JSON ---
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


data = load_data()

if not data:
    st.info("Chưa có dữ liệu từ vựng trong data.json.")
    st.stop()

# --- 2. THANH TÌM KIẾM ---
search_query = st.text_input("🔎 Nhập từ vựng hoặc nghĩa cần tìm:", "").strip().lower()

# --- 3. LỌC KẾT QUẢ ---
if search_query:
    filtered_data = {}
    for word, info in data.items():
        meaning = ""
        if isinstance(info, dict):
            meaning = info.get("meaning", info.get("definition", ""))
        else:
            meaning = str(info)

        # Tìm kiếm theo cả tên từ vựng lẫn nghĩa
        if search_query in word.lower() or search_query in meaning.lower():
            filtered_data[word] = info

    st.write(f"Tìm thấy **{len(filtered_data)}** kết quả:")
    st.divider()

    if filtered_data:
        for word, info in filtered_data.items():
            if isinstance(info, dict):
                meaning = info.get("meaning", info.get("definition", str(info)))
                correct = info.get("correct", 0)
                wrong = info.get("wrong", 0)
            else:
                meaning = str(info)
                correct = 0
                wrong = 0

            with st.container():
                st.subheader(f"📌 {word}")
                st.write(f"**Nghĩa:** {meaning}")
                st.caption(f"📊 Thống kê: **{correct}** đúng / **{wrong}** sai")
                st.divider()
    else:
        st.warning("Không tìm thấy từ vựng nào khớp với từ khóa.")
else:
    st.info("Hãy nhập từ khóa vào ô tìm kiếm ở trên.")