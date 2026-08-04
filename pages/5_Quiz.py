import streamlit as st
import json
import random

st.title("🎯 Quiz Mode")


# --- 1. HÀM ĐỌC & LƯU FILE DATA.JSON ---
def load_data():
    with open("data.json", "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


data = load_data()
all_words = list(data.keys())

# Kiểm tra xem đủ từ để làm Quiz trắc nghiệm không (cần ít nhất 4 từ để tạo 4 lựa chọn A, B, C, D)
if len(all_words) < 4:
    st.warning("⚠️ Bạn cần ít nhất 4 từ vựng trong data.json để bắt đầu Quiz Mode!")
    st.stop()


# --- 2. HÀM LẤY NGHĨA CỦA TỪ ---
def get_meaning(word):
    word_info = data[word]
    if isinstance(word_info, dict):
        return word_info.get("meaning", word_info.get("definition", str(word_info)))
    return str(word_info)


# --- 3. KHỞI TẠO TRẠNG THÁI QUIZ ---
TOTAL_QUESTIONS = min(20, len(all_words))  # Tối đa 20 câu hoặc bằng tổng số từ hiện có

if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

# Nút bắt đầu Quiz
if not st.session_state.quiz_started:
    st.info(f"Bài trắc nghiệm sẽ gồm **{TOTAL_QUESTIONS} câu hỏi**. Mỗi câu chọn 1 đáp án đúng nhất.")
    if st.button("🚀 Bắt đầu làm bài Quiz", type="primary"):
        # Chọn ngẫu nhiên danh sách câu hỏi cho phiên này
        quiz_words = random.sample(all_words, TOTAL_QUESTIONS)

        # Tạo danh sách các câu hỏi với 4 lựa chọn A, B, C, D
        questions = []
        for word in quiz_words:
            correct_meaning = get_meaning(word)

            # Lấy 3 nghĩa sai từ các từ khác
            other_words = [w for w in all_words if w != word]
            wrong_words_sample = random.sample(other_words, min(3, len(other_words)))
            wrong_meanings = [get_meaning(w) for w in wrong_words_sample]

            # Trộn lẫn đáp án
            options = wrong_meanings + [correct_meaning]
            random.shuffle(options)

            questions.append({
                "word": word,
                "correct_meaning": correct_meaning,
                "options": options
            })

        st.session_state.quiz_questions = questions
        st.session_state.quiz_index = 0
        st.session_state.quiz_score = 0
        st.session_state.quiz_wrong_words = []
        st.session_state.quiz_submitted = False
        st.session_state.quiz_finished = False
        st.session_state.quiz_started = True
        st.rerun()

# --- 4. MÀN HÌNH KẾT QUẢ CUỐI BÀI ---
elif st.session_state.get("quiz_finished", False):
    st.balloons()
    st.header("🏁 Kết quả bài kiểm tra")

    score = st.session_state.quiz_score
    total = TOTAL_QUESTIONS
    accuracy = (score / total) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Score", value=f"{score}/{total}")
    with col2:
        st.metric(label="Accuracy", value=f"{accuracy:.0f}%")

    st.subheader("Wrong words:")
    if st.session_state.quiz_wrong_words:
        for w in st.session_state.quiz_wrong_words:
            st.error(f"❌ **{w}**: {get_meaning(w)}")
    else:
        st.success("🎉 Xuất sắc! Bạn không sai từ nào.")

    if st.button("🔄 Làm bài Quiz mới"):
        st.session_state.quiz_started = False
        st.rerun()

# --- 5. GIAO DIỆN LÀM BÀI QUIZ ---
else:
    current_idx = st.session_state.quiz_index
    q = st.session_state.quiz_questions[current_idx]

    st.caption(f"Question {current_idx + 1}/{TOTAL_QUESTIONS}")
    st.subheader(f"**{q['word']}**")

    # Form trắc nghiệm
    selected_option = st.radio(
        "Chọn đáp án đúng:",
        options=q["options"],
        key=f"radio_{current_idx}",
        disabled=st.session_state.quiz_submitted  # Khoá không cho chọn lại sau khi Submit
    )

    st.write("")

    # Chưa Submit câu này
    if not st.session_state.quiz_submitted:
        if st.button("Submit", type="primary"):
            st.session_state.quiz_submitted = True

            # Kiểm tra đúng / sai
            is_correct = (selected_option == q["correct_meaning"])
            st.session_state.last_is_correct = is_correct

            # Lưu số lần đúng / sai vào data.json
            if isinstance(data[q["word"]], dict):
                if "correct" not in data[q["word"]]:
                    data[q["word"]]["correct"] = 0
                if "wrong" not in data[q["word"]]:
                    data[q["word"]]["wrong"] = 0

                if is_correct:
                    data[q["word"]]["correct"] += 1
                else:
                    data[q["word"]]["wrong"] += 1

            save_data(data)

            if is_correct:
                st.session_state.quiz_score += 1
            else:
                st.session_state.quiz_wrong_words.append(q["word"])

            st.rerun()

    # Đã Submit câu này -> Hiện phản hồi và nút Next
    else:
        if st.session_state.last_is_correct:
            st.success("✅ Correct!")
        else:
            st.error(f"❌ Incorrect! Đáp án đúng là: **{q['correct_meaning']}**")

        btn_label = "Next →" if current_idx + 1 < TOTAL_QUESTIONS else "Xem kết quả 🏁"
        if st.button(btn_label, type="primary"):
            st.session_state.quiz_submitted = False
            if current_idx + 1 < TOTAL_QUESTIONS:
                st.session_state.quiz_index += 1
            else:
                st.session_state.quiz_finished = True
            st.rerun()