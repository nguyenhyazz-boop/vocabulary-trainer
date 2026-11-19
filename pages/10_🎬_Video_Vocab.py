import re
from collections import Counter
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
from utils.data_manager import load_data, save_data

st.set_page_config(page_title="Video Vocab | Vocabulary Trainer", page_icon="🎬", layout="wide")

# Danh sách từ chức năng cơ bản (Stopwords) để lọc ra từ vựng đáng học
STOPWORDS = {
    "the", "and", "that", "have", "for", "not", "with", "you", "this", "but",
    "his", "from", "they", "say", "her", "she", "will", "one", "all", "would",
    "there", "their", "what", "out", "about", "who", "get", "which", "when",
    "make", "can", "like", "time", "just", "him", "know", "take", "people",
    "into", "year", "your", "good", "some", "could", "them", "see", "other",
    "than", "then", "now", "look", "only", "come", "its", "over", "think",
    "also", "back", "after", "use", "two", "how", "our", "work", "first",
    "well", "way", "even", "new", "want", "because", "any", "these", "give",
    "day", "most", "are", "was", "were", "been", "has", "had", "did", "does",
    "doing", "very", "more", "much", "many", "such", "those", "being", "here",
    "why", "where", "each", "both", "few", "own", "same", "too", "every"
}

def extract_video_id(url: str):
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",
        r"youtu\.be\/([0-9A-Za-z_-]{11})",
        r"shorts\/([0-9A-Za-z_-]{11})"
    ]
    for p in patterns:
        match = re.search(p, url)
        if match:
            return match.group(1)
    return None

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_youtube_transcript(video_id: str):
    try:
        # Hỗ trợ cả bản youtube-transcript-api mới lẫn cũ
        if hasattr(YouTubeTranscriptApi, "fetch"):
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
            segments = [{"text": s.text, "start": s.start} for s in transcript_list]
        else:
            raw = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
            segments = [{"text": s["text"], "start": s["start"]} for s in raw]
        return segments, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=86400, show_spinner=False)
def translate_to_vi(text: str):
    try:
        return GoogleTranslator(source="en", target="vi").translate(text)
    except Exception:
        return ""

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1050px !important;
    }
    .app-title {
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.4rem;
    }
    .transcript-box {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 20px;
        max-height: 360px;
        overflow-y: auto;
        line-height: 1.75;
        font-size: 1rem;
        color: #1E293B;
    }
    .time-badge {
        display: inline-block;
        background: #E0F2FE;
        color: #0369A1;
        font-size: 0.78rem;
        font-weight: 700;
        padding: 1px 6px;
        border-radius: 5px;
        margin-right: 6px;
        font-family: monospace;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🎬 Học Từ Vựng Qua Video YouTube</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Dán link video tiếng Anh bất kỳ để tự động bóc lời thoại (Transcript), lọc từ vựng hay và lưu vào kho học!</div>', unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# Tải kho từ hiện tại của user
vocab_data = load_data(f"data_vocab_{username}.json")
colloc_data = load_data(f"data_collocation_{username}.json")
if not isinstance(vocab_data, dict):
    vocab_data = {}
if not isinstance(colloc_data, dict):
    colloc_data = {}
user_all_words = {**vocab_data, **colloc_data}

# --- THANH NHẬP LINK YOUTUBE ---
col_url, col_btn = st.columns([4, 1])
with col_url:
    yt_url = st.text_input(
        "Link YouTube:",
        placeholder="Ví dụ: https://www.youtube.com/watch?v=...",
        label_visibility="collapsed"
    )
with col_btn:
    analyze_clicked = st.button("🔍 Bóc lời thoại", type="primary", use_container_width=True)

if yt_url:
    video_id = extract_video_id(yt_url.strip())
    if not video_id:
        st.error("Link YouTube chưa đúng định dạng. Hãy kiểm tra lại đường dẫn nhé!")
        st.stop()

    with st.spinner("Đang trích xuất lời thoại tiếng Anh từ video..."):
        segments, err = fetch_youtube_transcript(video_id)

    if err or not segments:
        st.warning("Video này chưa bật phụ đề tiếng Anh (CC) hoặc bị YouTube chặn truy cập tự động. Hãy thử một video học tiếng Anh khác (như TED-Ed, BBC Learning English) nhé!")
        st.stop()

    full_text = " ".join(seg["text"].replace("\n", " ") for seg in segments)

    # --- CHIA 2 CỘT: VIDEO + TRANSCRIPT | TRÍCH XUẤT & LƯU TỪ VỰNG ---
    left_col, right_col = st.columns([1.15, 1])

    with left_col:
        st.video(f"https://www.youtube.com/watch?v={video_id}")
        st.markdown("#### 📜 Lời thoại tự động (Transcript)")

        transcript_html = ""
        for seg in segments:
            mins = int(seg["start"] // 60)
            secs = int(seg["start"] % 60)
            t_str = f"{mins:02d}:{secs:02d}"
            clean_line = seg["text"].replace("\n", " ")
            transcript_html += f'<div style="margin-bottom: 8px;"><span class="time-badge">{t_str}</span>{clean_line}</div>'

        st.markdown(f'<div class="transcript-box">{transcript_html}</div>', unsafe_allow_html=True)

    with right_col:
        st.markdown("#### ✨ Nhặt từ vựng vào kho học")

        # Lọc các từ tiếng Anh dài >= 5 ký tự, không nằm trong stopwords và chưa có trong kho user
        raw_words = re.findall(r"\b[a-zA-Z]{5,}\b", full_text.lower())
        word_counts = Counter(w for w in raw_words if w not in STOPWORDS and w not in user_all_words)
        suggested_words = [w for w, _ in word_counts.most_common(40)]

        selected_from_list = st.multiselect(
            "1️⃣ Chọn từ hay hệ thống lọc được trong video:",
            options=suggested_words,
            default=suggested_words[:3] if len(suggested_words) >= 3 else suggested_words
        )

        custom_phrase = st.text_input(
            "2️⃣ Hoặc tự gõ từ / cụm từ (Collocation) bạn thấy hay trong lời thoại:",
            placeholder="Ví dụ: take into account, sustainable..."
        )

        words_to_process = list(dict.fromkeys(
            selected_from_list + ([custom_phrase.strip().lower()] if custom_phrase.strip() else [])
        ))

        topic_name = st.text_input("Tên chủ đề lưu trong kho:", value="YouTube Video")

        if words_to_process:
            st.divider()
            st.caption("Kiểm tra nghĩa tiếng Việt trước khi lưu:")

            for idx, w in enumerate(words_to_process):
                auto_vi = translate_to_vi(w)
                c1, c2, c3 = st.columns([1.3, 2, 1])
                with c1:
                    st.markdown(f"**{w}**")
                with c2:
                    edited_vi = st.text_input(
                        f"Nghĩa của {w}",
                        value=auto_vi,
                        key=f"vi_{video_id}_{w}_{idx}",
                        label_visibility="collapsed"
                    )
                with c3:
                    if w in user_all_words:
                        st.success("Đã lưu")
                    else:
                        if st.button("➕ Lưu", key=f"save_{video_id}_{w}_{idx}", use_container_width=True):
                            is_phrase = " " in w.strip()
                            target_file = f"data_collocation_{username}.json" if is_phrase else f"data_vocab_{username}.json"
                            repo = load_data(target_file)
                            if not isinstance(repo, dict):
                                repo = {}
                            repo[w] = {
                                "meaning": edited_vi.strip() or auto_vi,
                                "topic": topic_name.strip() or "YouTube Video",
                                "correct": 0,
                                "wrong": 0
                            }
                            save_data(repo, target_file)
                            st.toast(f"Đã lưu '{w}' vào kho!")
                            st.rerun()
        else:
            st.info("Chọn từ ở danh sách trên hoặc nhập cụm từ bạn muốn lưu từ đoạn thoại bên trái.")
else:
    st.info("👆 Hãy dán một đường dẫn video YouTube tiếng Anh vào ô phía trên để bắt đầu!")
