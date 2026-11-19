import streamlit as st
from utils.data_manager import load_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Statistics | Vocabulary Trainer", page_icon="📊", layout="wide")
apply_global_theme("2_Statistics")

# --- CUSTOM CSS: WARM EDITORIAL ANALYTICS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.6rem;
        padding-bottom: 3rem;
        max-width: 1080px !important;
    }

    .stats-header {
        margin-bottom: 1.4rem;
    }
    .stats-sub {
        font-size: 0.82rem;
        font-weight: 700;
        color: #78716C;
        letter-spacing: 0.6px;
        text-transform: uppercase;
    }
    .stats-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }

    /* 4 Thẻ KPI phong cách Editorial */
    .kpi-card {
        border-radius: 18px;
        padding: 20px 22px;
        height: 145px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.18s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
    }
    .kpi-cream {
        background-color: #EFECE3;
        border: 1px solid #E5DFD2;
        color: #1C1917;
    }
    .kpi-yellow {
        background-color: #FACC15;
        color: #1C1917;
    }
    .kpi-purple {
        background-color: #7C3AED;
        color: #FFFFFF;
    }
    .kpi-white {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        color: #1C1917;
    }
    .kpi-num {
        font-size: 0.78rem;
        font-weight: 700;
        opacity: 0.75;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        line-height: 1.1;
        letter-spacing: -0.6px;
    }
    .kpi-label {
        font-size: 0.85rem;
        font-weight: 600;
        opacity: 0.85;
    }

    /* Khung Section trắng kem */
    .panel-box {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 20px;
        padding: 22px 24px;
        margin-bottom: 16px;
    }
    .panel-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #1C1917;
        margin-bottom: 4px;
    }
    .panel-desc {
        font-size: 0.84rem;
        color: #78716C;
        margin-bottom: 16px;
    }

    /* Thanh biểu đồ ngang tùy chỉnh */
    .bar-row {
        margin-bottom: 14px;
    }
    .bar-meta {
        display: flex;
        justify-content: space-between;
        font-size: 0.86rem;
        font-weight: 700;
        color: #1C1917;
        margin-bottom: 5px;
    }
    .bar-track {
        width: 100%;
        height: 9px;
        background-color: #F3EFE6;
        border-radius: 99px;
        overflow: hidden;
    }
    .bar-fill {
        height: 100%;
        border-radius: 99px;
    }

    /* Thẻ từ yếu cần ôn lại */
    .weak-item {
        background-color: #FAF8F2;
        border: 1px solid #E7E2D6;
        border-radius: 14px;
        padding: 12px 16px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .weak-word {
        font-size: 1rem;
        font-weight: 800;
        color: #1C1917;
    }
    .weak-meaning {
        font-size: 0.83rem;
        color: #78716C;
    }
    .weak-badge {
        background-color: #FEE2E2;
        color: #DC2626;
        font-size: 0.76rem;
        font-weight: 800;
        padding: 4px 10px;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username

# --- 1. TẢI & HỢP NHẤT DỮ LIỆU ---
colloc_data = load_data(f"data_collocation_{username}.json")
vocab_data = load_data(f"data_vocab_{username}.json")

if not isinstance(colloc_data, dict):
    colloc_data = {}
if not isinstance(vocab_data, dict):
    vocab_data = {}

all_words = {**vocab_data, **colloc_data}
total_words = len(all_words)

st.markdown("""
<div class="stats-header">
    <div class="stats-sub">Memory & Retention Analytics</div>
    <div class="stats-title">Learning Statistics</div>
</div>
""", unsafe_allow_html=True)

if total_words == 0:
    st.info("Kho từ vựng của bạn hiện đang trống! Hãy sang mục Add Word để bắt đầu lưu từ nhé.")
    st.stop()

# --- 2. PHÂN TÍCH MỨC ĐỘ GHI NHỚ & LOẠI TỪ ---
mastered_count = 0
learning_count = 0
unseen_count = 0
total_correct = 0
total_wrong = 0

pos_counts = {}
weak_list = []

for word, item in all_words.items():
    if isinstance(item, dict):
        c = item.get("correct", 0)
        w = item.get("wrong", 0)
        meaning = item.get("meaning", item.get("definition", ""))
        raw_pos = str(item.get("pos", "Other")).strip() or "Other"
    else:
        c, w, meaning, raw_pos = 0, 0, str(item), "Other"

    total_correct += c
    total_wrong += w
    attempts = c + w

    # Phân loại độ thuộc lòng
    if attempts == 0:
        unseen_count += 1
    elif c >= 3 and (c / attempts) >= 0.8:
        mastered_count += 1
    else:
        learning_count += 1

    # Gom nhóm loại từ (tự nhận diện Collocation nếu có >= 2 từ)
    if word in colloc_data or len(word.strip().split()) >= 2 or "colloc" in raw_pos.lower():
        pos_label = "Collocation / Phrase"
    else:
        pos_label = raw_pos.capitalize()
    pos_counts[pos_label] = pos_counts.get(pos_label, 0) + 1

    # Lọc danh sách từ hay sai hoặc độ chính xác thấp
    if w > 0:
        acc_word = round((c / attempts) * 100) if attempts > 0 else 0
        weak_list.append({
            "word": word,
            "meaning": meaning,
            "wrong": w,
            "correct": c,
            "acc": acc_word
        })

overall_acc = round((total_correct / (total_correct + total_wrong)) * 100) if (total_correct + total_wrong) > 0 else 0

# --- 3. HÀNG 4 THẺ KPI ---
k1, k2, k3, k4 = st.columns(4, gap="medium")

with k1:
    st.markdown(f"""
    <div class="kpi-card kpi-cream">
        <div class="kpi-num">01 · TOTAL VAULT</div>
        <div class="kpi-value">{total_words}</div>
        <div class="kpi-label">Stored words & phrases</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card kpi-yellow">
        <div class="kpi-num">02 · MASTERED</div>
        <div class="kpi-value">{mastered_count}</div>
        <div class="kpi-label">≥ 80% recall accuracy</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card kpi-purple">
        <div class="kpi-num">03 · LEARNING</div>
        <div class="kpi-value">{learning_count}</div>
        <div class="kpi-label">In active review cycle</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card kpi-white">
        <div class="kpi-num">04 · UNSEEN</div>
        <div class="kpi-value">{unseen_count}</div>
        <div class="kpi-label">Not yet practiced</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# --- 4. CHIA 2 CỘT PHÂN TÍCH CHI TIẾT ---
col_left, col_right = st.columns([1.15, 1], gap="large")

with col_left:
    # Khối 1: Tỷ lệ thành thạo tổng thể
    st.markdown(f"""
    <div class="panel-box">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div class="panel-title">Retention Breakdown</div>
                <div class="panel-desc">Overall recall accuracy: <b>{overall_acc}%</b> ({total_correct} correct / {total_wrong} wrong)</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    stages = [
        ("Mastered (Long-term)", mastered_count, "#7C3AED"),
        ("In Progress (Learning)", learning_count, "#FACC15"),
        ("New / Unseen", unseen_count, "#1C1917"),
    ]
    for label, count, color in stages:
        pct = round((count / total_words) * 100) if total_words > 0 else 0
        st.markdown(f"""
        <div class="bar-row">
            <div class="bar-meta">
                <span>{label}</span>
                <span>{count} words ({pct}%)</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%; background-color:{color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Khối 2: Phân bổ theo loại từ (Part of Speech)
    st.markdown("""
    <div class="panel-box">
        <div class="panel-title">Vocabulary Composition</div>
        <div class="panel-desc">Distribution by part of speech & collocations</div>
    """, unsafe_allow_html=True)

    sorted_pos = sorted(pos_counts.items(), key=lambda x: x[1], reverse=True)
    palette = ["#1C1917", "#7C3AED", "#EAB308", "#0D9488", "#EA580C"]
    for idx, (pos_name, count) in enumerate(sorted_pos):
        pct = round((count / total_words) * 100) if total_words > 0 else 0
        bar_color = palette[idx % len(palette)]
        st.markdown(f"""
        <div class="bar-row">
            <div class="bar-meta">
                <span>{pos_name}</span>
                <span>{count} ({pct}%)</span>
            </div>
            <div class="bar-track">
                <div class="bar-fill" style="width:{pct}%; background-color:{bar_color};"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown("""
    <div class="panel-box">
        <div class="panel-title">Priority Review Words</div>
        <div class="panel-desc">Words with the highest miss rate that need reinforcement</div>
    """, unsafe_allow_html=True)

    if weak_list:
        weak_sorted = sorted(weak_list, key=lambda x: (-x["wrong"], x["acc"]))[:6]
        for item in weak_sorted:
            st.markdown(f"""
            <div class="weak-item">
                <div>
                    <div class="weak-word">{item['word']}</div>
                    <div class="weak-meaning">{item['meaning']}</div>
                </div>
                <div style="text-align:right;">
                    <span class="weak-badge">{item['wrong']} wrong · {item['acc']}%</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        if st.button("Practice These Weak Words Now  ↗", type="primary", use_container_width=True):
            st.session_state.batch_words = [x["word"] for x in weak_sorted]
            st.session_state.studied_words = []
            if "current_word" in st.session_state:
                del st.session_state.current_word
            st.switch_page("pages/1_Study.py")
    else:
        st.markdown("""
        <div style="background:#F3EFE6; border-radius:14px; padding:24px; text-align:center; color:#57534E;">
            <div style="font-size:1.05rem; font-weight:700; color:#1C1917; margin-bottom:4px;">Zero Weak Words</div>
            <div style="font-size:0.86rem;">Bạn chưa làm sai từ nào cả. Tiếp tục duy trì phong độ nhé!</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
