import re
import random
import streamlit as st
from utils.data_manager import load_data, save_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Quiz Arena | Vocabulary Trainer", page_icon="⚡", layout="wide")
apply_global_theme("5_Quiz")

# --- CUSTOM CSS: WARM EDITORIAL QUIZ ARENA ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 760px !important;
    }

    .quiz-sub {
        font-size: 0.82rem;
        font-weight: 700;
        color: #78716C;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .quiz-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }

    /* Thanh chỉ số Streak & Score đồng bộ Dashboard */
    .quiz-stats-bar {
        display: flex;
        justify-content: flex-end;
        gap: 8px;
        margin-top: 10px;
    }
    .stat-pill {
        background: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 0.83rem;
        font-weight: 700;
        color: #1C1917;
        display: inline-flex;
        align-items: center;
        gap: 6px;
    }
    .dot-orange { width: 8px; height: 8px; border-radius: 50%; background: #EA580C; display: inline-block; }
    .dot-purple { width: 8px; height: 8px; border-radius: 50%; background: #7C3AED; display: inline-block; }

    /* Thẻ câu hỏi 2 lớp Editorial */
    .quiz-shell {
        background-color: #EFECE3;
        border: 1px solid #E5DFD2;
        border-radius: 24px;
        padding: 16px;
        margin-top: 14px;
        margin-bottom: 20px;
    }
    .quiz-inner {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 18px;
        padding: 40px 24px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(28, 25, 23, 0.04);
    }

    .badge-colloc {
        display: inline-block;
        background-color: #EDE9FE;
        color: #7C3AED;
        border: 1px solid #DDD6FE;
        font-size: 0.72rem;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }
    .badge-vocab {
        display: inline-block;
        background-color: #F3EFE6;
        color: #78716C;
        border: 1px solid #E7E2D6;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-bottom: 10px;
    }
    .quiz-word {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        line-height: 1.2;
    }
    .quiz-pos {
        font-size: 0.92rem;
        font-weight: 600;
        color: #78716C;
        margin-top: 6px;
    }

    /* Nút đáp án trắc nghiệm lớn, sang trọng */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background-color: #FFFFFF !important;
        color: #1C1917 !important;
        border: 1px solid #DCD6C8 !important;
        border-radius: 14px !important;
        padding: 0.85rem 1rem !important;
        font-size: 1.02rem !important;
        font-weight: 700 !important;
        min-height: 58px !important;
        box-shadow: 0 2px 6px rgba(28, 25, 23, 0.03) !important;
    }
    div[data-testid="stHorizontalBlock"] .stButton > button:hover {
        background-color: #EFECE3 !important;
        border-color: #1C1917 !important;
        transform: translateY(-2px);
    }

    /* Thẻ kết quả phản hồi */
    .result-box-ok {
        background-color: #F0FDF4;
        border: 1px solid #BBF7D0;
        color: #166534;
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .result-box-err {
        background-color: #FEF2F2;
        border: 1px solid #FECACA;
        color: #991B1B;
        border-radius: 16px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username

if "streak" not in st.session_state:
    st.session_state.streak = 0
if "score" not in st.session_state:
    st.session_state.score = 0

# --- 1. TẢI & GỘP DỮ LIỆU TỪ CẢ HAI KHO ---
vocab_file = f"data_vocab_{username}.json"
colloc_file = f"data_collocation_{username}.json"

vocab_data = load_data(vocab_file)
colloc_data = load_data(colloc_file)

if not isinstance(vocab_data, dict):
    vocab_data = {}
if not isinstance(colloc_data, dict):
    colloc_data = {}

combined_data = {}
word_source_map = {}

for w, info in vocab_data.items():
    combined_data[w] = info
    word_source_map[w] = "vocab"

for w, info in colloc_data.items():
    combined_data[w] = info
    word_source_map[w] = "colloc"

all_words = list(combined_data.keys())

# --- THANH TIÊU ĐỀ & CHỈ SỐ STREAK / SCORE ---
head_col1, head_col2 = st.columns([1.4, 1])
with head_col1:
    st.markdown("""
    <div class="quiz-sub">Rapid Recall Challenge</div>
    <div class="quiz-title">Quiz Arena</div>
    """, unsafe_allow_html=True)

with head_col2:
    st.markdown(f"""
    <div class="quiz-stats-bar">
        <span class="stat-pill"><span class="dot-orange"></span> Streak: {st.session_state.streak}</span>
        <span class="stat-pill"><span class="dot-purple"></span> {st.session_state.score} pts</span>
    </div>
    """, unsafe_allow_html=True)

if not all_words:
    st.write("")
    st.info("Kho từ vựng của bạn hiện đang trống! Hãy sang mục Add Word hoặc Library để thêm từ nhé.")
    st.stop()

def is_collocation_item(word: str, info) -> bool:
    if word_source_map.get(word) == "colloc":
        return True
    if isinstance(info, dict):
        pos_val = str(info.get("pos", "")).lower()
        if "colloc" in pos_val or "phrase" in pos_val or "idiom" in pos_val:
            return True
    return len(word.strip().split()) >= 2

# --- 2. CHỌN TỪ VỰNG NGẪU NHIÊN ---
if "quiz_word" not in st.session_state or st.session_state.quiz_word not in all_words:
    st.session_state.quiz_word = random.choice(all_words)
    st.session_state.answered = False

target_word = st.session_state.quiz_word
word_info = combined_data[target_word]

if isinstance(word_info, dict):
    correct_meaning = word_info.get("meaning", word_info.get("definition", str(word_info)))
    pos_tag = word_info.get("pos", "")
    example_text = word_info.get("example", "").strip()
else:
    correct_meaning = str(word_info)
    pos_tag = ""
    example_text = ""

# --- 3. TẠO 4 ĐÁP ÁN TRẮC NGHIỆM ---
if "options" not in st.session_state or st.session_state.get("current_target") != target_word:
    other_meanings = []
    for w, item in combined_data.items():
        if w != target_word:
            m = item.get("meaning", item.get("definition", str(item))) if isinstance(item, dict) else str(item)
            if m and m != correct_meaning and m not in other_meanings:
                other_meanings.append(m)

    default_fakes = [
        "nghiên cứu kỹ lưỡng",
        "tạo ra sự khác biệt",
        "thực hiện kế hoạch",
        "giữ liên lạc thường xuyên",
        "đưa ra quyết định quan trọng",
        "giải quyết vấn đề hiệu quả"
    ]
    for f in default_fakes:
        if len(other_meanings) < 3 and f != correct_meaning and f not in other_meanings:
            other_meanings.append(f)

    selected_fakes = random.sample(other_meanings, min(3, len(other_meanings)))
    opts = selected_fakes + [correct_meaning]
    random.shuffle(opts)

    st.session_state.options = opts
    st.session_state.current_target = target_word

# --- 4. HIỂN THỊ THẺ CÂU HỎI ---
badge_html = (
    '<div class="badge-colloc">Collocation</div>'
    if is_collocation_item(target_word, word_info)
    else '<div class="badge-vocab">Vocabulary</div>'
)
pos_html = f'<div class="quiz-pos">{pos_tag}</div>' if pos_tag else ""

st.markdown(f"""
<div class="quiz-shell">
    <div class="quiz-inner">
        {badge_html}
        <div class="quiz-word">{target_word}</div>
        {pos_html}
    </div>
</div>
""", unsafe_allow_html=True)

# --- 5. XỬ LÝ ĐÁP ÁN & HIỂN THỊ LỰA CHỌN 2x2 ---
def check_answer(selected_option):
    st.session_state.answered = True
    source = word_source_map.get(target_word, "vocab")
    target_dict = colloc_data if source == "colloc" else vocab_data
    target_file = colloc_file if source == "colloc" else vocab_file

    if selected_option == correct_meaning:
        st.session_state.streak += 1
        st.session_state.score += 10
        st.session_state.last_result = ("correct", selected_option)

        if target_word in target_dict and isinstance(target_dict[target_word], dict):
            target_dict[target_word]["correct"] = target_dict[target_word].get("correct", 0) + 1
            save_data(target_dict, target_file)

        if st.session_state.streak % 5 == 0:
            st.balloons()
    else:
        st.session_state.streak = 0
        st.session_state.last_result = ("wrong", selected_option)

        if target_word in target_dict and isinstance(target_dict[target_word], dict):
            target_dict[target_word]["wrong"] = target_dict[target_word].get("wrong", 0) + 1
            save_data(target_dict, target_file)

if not st.session_state.get("answered", False):
    st.markdown('<div style="font-size:0.88rem; font-weight:700; color:#57534E; margin-bottom:10px;">Select the matching Vietnamese meaning:</div>', unsafe_allow_html=True)
    row1_col1, row1_col2 = st.columns(2, gap="medium")
    row2_col1, row2_col2 = st.columns(2, gap="medium")
    grid_cols = [row1_col1, row1_col2, row2_col1, row2_col2]

    for idx, opt in enumerate(st.session_state.options):
        with grid_cols[idx]:
            if st.button(opt, key=f"btn_opt_{idx}", use_container_width=True):
                check_answer(opt)
                st.rerun()
else:
    res_type, selected_opt = st.session_state.last_result

    ex_html = ""
    if example_text:
        clean_ex = example_text
        if target_word.lower() in clean_ex.lower() and "<b>" not in clean_ex.lower():
            pattern = re.compile(re.escape(target_word), re.IGNORECASE)
            clean_ex = pattern.sub(lambda m: f"<b>{m.group(0)}</b>", clean_ex)
        ex_html = f'<div style="margin-top:8px; padding-top:8px; border-top:1px dashed rgba(0,0,0,0.12); font-style:italic; font-size:0.95rem;">"{clean_ex}"</div>'

    if res_type == "correct":
        st.markdown(f"""
        <div class="result-box-ok">
            <div style="font-weight:800; font-size:1.05rem;">Correct! +10 pts</div>
            <div style="margin-top:2px;"><b>{target_word}</b> means <b>{correct_meaning}</b></div>
            {ex_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="result-box-err">
            <div style="font-weight:800; font-size:1.05rem;">Not quite — You selected: {selected_opt}</div>
            <div style="margin-top:2px;">Correct meaning of <b>{target_word}</b>: <b>{correct_meaning}</b></div>
            {ex_html}
        </div>
        """, unsafe_allow_html=True)

    if st.button("Next Question  ↗", type="primary", use_container_width=True):
        others = [w for w in all_words if w != target_word]
        st.session_state.quiz_word = random.choice(others) if others else target_word
        st.session_state.answered = False
        st.rerun()
