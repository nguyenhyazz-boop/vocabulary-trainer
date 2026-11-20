import re
import json
from collections import Counter
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from utils.data_manager import load_data, save_data
from utils.ui_theme import apply_global_theme

st.set_page_config(page_title="Video Vocab | Vocabulary Trainer", page_icon="📖", layout="wide")
apply_global_theme("10_Video_Vocab")

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
        match = re.search(p, url or "")
        if match:
            return match.group(1)
    return None

def call_gemini_text(prompt: str, api_key: str) -> str:
    if not api_key:
        return ""
    try:
        import requests
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        list_res = requests.get(list_url, timeout=10)
        exclude_kw = ("exp", "thinking", "audio", "image", "tts", "vision", "embedding", "aqa")
        candidates = []
        if list_res.status_code == 200:
            for m in list_res.json().get("models", []):
                m_name = m.get("name", "")
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    if "gemini" in m_name.lower() and not any(k in m_name.lower() for k in exclude_kw):
                        candidates.append(m_name.replace("models/", ""))
        candidates.sort(key=lambda x: (0 if "flash" in x else 1, x))
        if not candidates:
            candidates = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

        for model_name in candidates[:4]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3}
                }
                res = requests.post(url, json=payload, timeout=20)
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                    if text:
                        return text
            except Exception:
                continue
    except Exception:
        pass
    return ""

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_youtube_transcript(video_id: str):
    try:
        if hasattr(YouTubeTranscriptApi, "fetch"):
            api = YouTubeTranscriptApi()
            try:
                transcript_list = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
                segments = [{"text": s.text, "start": s.start} for s in transcript_list]
                if segments:
                    return segments, "Official / Auto Captions"
            except Exception:
                transcript_obj = api.list(video_id)
                for tr in transcript_obj:
                    try:
                        translated = tr.translate("en").fetch()
                        segments = [{"text": s.text, "start": s.start} for s in translated]
                        if segments:
                            return segments, "Translated Captions -> EN"
                    except Exception:
                        continue
        else:
            try:
                raw = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
                segments = [{"text": s["text"], "start": s["start"]} for s in raw]
                if segments:
                    return segments, "Official / Auto Captions"
            except Exception:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for tr in transcript_list:
                    try:
                        translated = tr.translate("en").fetch()
                        segments = [{"text": s["text"], "start": s["start"]} for s in translated]
                        if segments:
                            return segments, "Translated Captions -> EN"
                    except Exception:
                        continue
    except Exception:
        pass
    return None, None

@st.cache_data(ttl=86400, show_spinner=False)
def translate_words_batch_vi(words_tuple: tuple, gemini_key: str) -> dict:
    words_list = list(words_tuple)
    if not words_list:
        return {}

    result_map = {}
    if gemini_key:
        prompt = (
            f"Translate each English word or phrase in this list into concise Vietnamese meaning (1-4 words each). "
            f"Return ONLY valid JSON object mapping each exact word to its Vietnamese meaning:\n{json.dumps(words_list, ensure_ascii=False)}"
        )
        raw = call_gemini_text(prompt, gemini_key)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                parsed = json.loads(m.group(0))
                if isinstance(parsed, dict):
                    for k, v in parsed.items():
                        result_map[str(k).lower().strip()] = str(v).strip()
            except Exception:
                pass

    for w in words_list:
        wl = w.lower().strip()
        if not result_map.get(wl):
            try:
                from deep_translator import GoogleTranslator
                result_map[wl] = GoogleTranslator(source="en", target="vi").translate(w) or ""
            except Exception:
                result_map[wl] = ""

    return result_map

# --- CUSTOM CSS: WARM EDITORIAL VIDEO VOCAB ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.8rem;
        max-width: 1020px !important;
    }
    .vid-sub {
        font-size: 0.8rem;
        font-weight: 700;
        color: #78716C;
        letter-spacing: 0.7px;
        text-transform: uppercase;
    }
    .vid-title {
        font-size: 2rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.6px;
        margin-top: 2px;
    }
    .vid-desc {
        color: #57534E;
        font-size: 0.94rem;
        margin-top: 4px;
        margin-bottom: 1.2rem;
    }

    .transcript-box {
        background-color: #FAF8F2;
        border: 1px solid #E7E2D6;
        border-radius: 14px;
        padding: 14px 16px;
        max-height: 340px;
        overflow-y: auto;
        line-height: 1.72;
        font-size: 0.96rem;
        color: #1C1917;
        margin-top: 10px;
    }
    .time-badge {
        display: inline-block;
        background-color: #EDE9FE;
        color: #7C3AED;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 1px 7px;
        border-radius: 6px;
        margin-right: 8px;
        font-family: monospace;
    }
    .source-pill {
        display: inline-block;
        background-color: #EFECE3;
        color: #57534E;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        margin: 8px 0;
    }

    span[data-baseweb="tag"] {
        background-color: #EFECE3 !important;
        color: #1C1917 !important;
        border: 1px solid #DFD9C8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] span {
        color: #1C1917 !important;
    }
    span[data-baseweb="tag"] svg {
        fill: #57534E !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div>
    <div class="vid-sub">Video Transcript & Lyrics Vocab</div>
    <div class="vid-title">YouTube Video Vocab</div>
    <div class="vid-desc">Lấy phụ đề CC thật từ video YouTube hoặc dán lời bài hát / lời thoại để lọc từ vựng chính xác</div>
</div>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "").strip()

vocab_data = load_data(f"data_vocab_{username}.json")
colloc_data = load_data(f"data_collocation_{username}.json")
if not isinstance(vocab_data, dict):
    vocab_data = {}
if not isinstance(colloc_data, dict):
    colloc_data = {}
user_all_words = {**vocab_data, **colloc_data}

# --- THANH NHẬP LINK YOUTUBE ---
col_url, col_btn = st.columns([4, 1.15], gap="small")
with col_url:
    yt_url = st.text_input(
        "Link YouTube",
        placeholder="Paste YouTube link (e.g. https://www.youtube.com/watch?v=...)",
        label_visibility="collapsed"
    )
with col_btn:
    st.button("Load Video  ↗", type="primary", use_container_width=True)

segments = []
source_label = ""
cc_missing = False
video_id = extract_video_id(yt_url.strip()) if yt_url else None

if yt_url and not video_id:
    st.error("Link YouTube chưa đúng định dạng. Hãy kiểm tra lại đường dẫn nhé!")
    st.stop()

if video_id:
    with st.spinner("Đang kiểm tra phụ đề CC từ YouTube..."):
        cc_segments, cc_mode = fetch_youtube_transcript(video_id)
    if cc_segments:
        segments = cc_segments
        source_label = cc_mode
    else:
        cc_missing = True

with st.expander("Dán lời bài hát (Lyrics) hoặc lời thoại thủ công", expanded=cc_missing or not bool(segments)):
    if cc_missing:
        st.info("Video/bài hát này chưa có phụ đề CC tự động hoặc bị YouTube chặn lấy phụ đề trên Cloud. Hãy dán lời bài hát / lời thoại vào ô dưới để lọc từ vựng chuẩn xác nhất!")
    manual_script = st.text_area(
        "Dán lyrics hoặc transcript tiếng Anh vào đây:",
        placeholder="Paste song lyrics or transcript here...",
        height=130
    )
    if manual_script.strip():
        lines = [line.strip() for line in re.split(r"\n+", manual_script.strip()) if line.strip()]
        segments = [{"text": line, "start": i * 5} for i, line in enumerate(lines)]
        source_label = "Manual Lyrics / Transcript"

if segments:
    full_text = " ".join(seg["text"].replace("\n", " ") for seg in segments)

    left_col, right_col = st.columns([1.15, 1], gap="large")

    with left_col:
        with st.container(border=True):
            st.caption("SOURCE PLAYER & SCRIPT")
            if video_id:
                st.video(f"https://www.youtube.com/watch?v={video_id}")
            st.markdown(f'<span class="source-pill">{source_label}</span>', unsafe_allow_html=True)

            transcript_html = "".join(
                f'<div style="margin-bottom:8px;"><span class="time-badge">{int(seg["start"] // 60):02d}:{int(seg["start"] % 60):02d}</span>{seg["text"].replace(chr(10), " ")}</div>'
                for seg in segments
            )
            st.markdown(f'<div class="transcript-box">{transcript_html}</div>', unsafe_allow_html=True)

    with right_col:
        with st.container(border=True):
            st.caption("VOCABULARY PICKER")
            st.markdown("#### Nhặt từ vựng vào kho học")

            raw_words = re.findall(r"\b[a-zA-Z]{4,}\b", full_text.lower())
            word_counts = Counter(w for w in raw_words if w not in STOPWORDS and w not in user_all_words)
            suggested_words = [w for w, _ in word_counts.most_common(40)]

            default_picks = suggested_words[:3] if len(suggested_words) >= 3 else suggested_words
            selected_from_list = st.multiselect(
                "1. Chọn từ hay hệ thống lọc được:",
                options=suggested_words,
                default=default_picks
            )

            custom_phrase = st.text_input(
                "2. Hoặc nhập từ / cụm từ (Collocation) bạn thấy hay:",
                placeholder="e.g. beauty and a beat, take into account..."
            )

            words_to_process = list(dict.fromkeys(
                selected_from_list + ([custom_phrase.strip().lower()] if custom_phrase.strip() else [])
            ))

            topic_name = st.text_input("Chủ đề lưu trong kho:", value="YouTube Video")

            if words_to_process:
                st.divider()
                st.caption("Nghĩa tiếng Việt tự động dịch (bạn có thể sửa lại trước khi lưu):")
                vi_map = translate_words_batch_vi(tuple(words_to_process), gemini_api_key)

                for idx, w in enumerate(words_to_process):
                    auto_vi = vi_map.get(w.lower().strip(), "")
                    c1, c2, c3 = st.columns([1.25, 2.1, 1])
                    with c1:
                        st.markdown(f"**{w}**")
                    with c2:
                        edited_vi = st.text_input(
                            f"Nghĩa của {w}",
                            value=auto_vi,
                            key=f"vi_{video_id or 'manual'}_{w}_{idx}",
                            label_visibility="collapsed"
                        )
                    with c3:
                        if w in user_all_words:
                            st.markdown('<span class="source-pill">Saved</span>', unsafe_allow_html=True)
                        else:
                            if st.button("Save", key=f"save_{video_id or 'manual'}_{w}_{idx}", use_container_width=True):
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
                st.info("Chọn từ ở danh sách trên hoặc nhập cụm từ bạn muốn lưu từ phần lời bên trái.")
else:
    st.info("Hãy dán link YouTube có phụ đề CC hoặc mở phần dán lời bài hát / lời thoại thủ công để bắt đầu.")
