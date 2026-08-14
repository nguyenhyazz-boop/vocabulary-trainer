import streamlit as st
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Library | Vocabulary Trainer", page_icon="📚", layout="wide")

# --- CUSTOM CSS: GIAO DIỆN LIBRARY CHUẨN MODERN UI ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }
    
    .app-title {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #1E293B;
        letter-spacing: -0.5px;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Stat Box */
    .stat-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #0F172A;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 500;
    }

    /* Badges */
    .pos-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-noun { background-color: #E0F2FE; color: #0369A1; }
    .badge-verb { background-color: #DCFCE7; color: #15803D; }
    .badge-adj { background-color: #FEF9C3; color: #A16207; }
    .badge-adv { background-color: #F3E8FF; color: #7E22CE; }
    .badge-phrase { background-color: #FFEDD5; color: #C2410C; }
    .badge-other { background-color: #F1F5F9; color: #475569; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
<div>
    <div class="app-title">Vocabulary Library</div>
    <div class="app-subtitle">Thư viện tổng hợp và phân loại toàn bộ kho từ vựng cá nhân</div>
</div>
""", unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

vocab_file = f"data_vocab_{username}.json"
colloc_file = f"data_collocation_{username}.json"

vocab_data = load_data(vocab_file)
if not isinstance(vocab_data, dict): vocab_data = {}

colloc_data = load_data(colloc_file)
if not isinstance(colloc_data, dict): colloc_data = {}

# --- THỐNG KÊ NHANH (METRICS DASHBOARD) ---
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(vocab_data)}</div>
        <div class="stat-label">Từ đơn (Normal Vocab)</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(colloc_data)}</div>
        <div class="stat-label">Cụm từ (Collocations)</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="stat-card">
        <div class="stat-number">{len(vocab_data) + len(colloc_data)}</div>
        <div class="stat-label">Tổng kho từ vựng</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.divider()

# --- DANH SÁCH CHI TIẾT THEO TAB ---
tab_vocab, tab_colloc = st.tabs(["📚 Từ đơn (Normal Vocab)", "🔗 Cụm từ (Collocations)"])

def render_vocabulary_list(data_dict, target_file):
    if not data_dict:
        st.info("Kho từ vựng này hiện đang trống. Hãy sang mục **Add Word** để thêm từ mới nhé!")
        return

    st.write("")
    for word, info in list(data_dict.items()):
        pos = info.get("pos", "Other")
        meaning = info.get("meaning", "N/A")
        example = info.get("example", "")
        correct = info.get("correct", 0)
        wrong = info.get("wrong", 0)

        pos_key = pos.lower()
        badge_class = f"badge-{pos_key}" if pos_key in ["noun", "verb", "adj", "adv", "phrase"] else "badge-other"

        with st.expander(f"📌 **{word}** — {meaning}"):
            col_info, col_act = st.columns([4, 1])
            with col_info:
                st.markdown(f"**Loại từ:** <span class='pos-badge {badge_class}'>{pos}</span>", unsafe_allow_html=True)
                if example:
                    st.write(f"**Ví dụ:** *\"{example}\"*")
                st.caption(f"🎯 Đã trả lời đúng: **{correct}** lần | ❌ Trả lời sai: **{wrong}** lần")

            with col_act:
                if st.button("🗑️ Xóa từ", key=f"lib_del_{target_file}_{word}", use_container_width=True):
                    del data_dict[word]
                    save_data(data_dict, target_file)
                    st.success(f"Đã xóa '{word}'")
                    st.rerun()

with tab_vocab:
    render_vocabulary_list(vocab_data, vocab_file)

with tab_colloc:
    render_vocabulary_list(colloc_data, colloc_file)
