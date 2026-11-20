import re
import json
import urllib.parse
import requests
from collections import Counter
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
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

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_youtube_transcript(video_id: str):
    try:
        if hasattr(YouTubeTranscriptApi, "fetch"):
            api = YouTubeTranscriptApi()
            try:
                transcript_list = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
                segments = [{"text": s.text, "start": s.start} for s in transcript_list]
                return segments, "cc_en", None
            except Exception:
                # Thử lấy danh sách phụ đề khả dụng và dịch sang tiếng Anh nếu có
                transcript_obj = api.list(video_id)
                for tr in transcript_obj:
                    try:
                        translated = tr.translate("en").fetch()
                        segments = [{"text": s.text, "start": s.start} for s in translated]
                        if segments:
                            return segments, "cc_translated", None
                    except Exception:
                        continue
        else:
            try:
                raw = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
                segments = [{"text": s["text"], "start": s["start"]} for s in raw]
                return segments, "cc_en", None
            except Exception:
                transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                for tr in transcript_list:
                    try:
                        translated = tr.translate("en").fetch()
                        segments = [{"text": s["text"], "start": s["start"]} for s in translated]
                        if segments:
                            return segments, "cc_translated", None
                    except Exception:
                        continue
        return None, None, "No caption available"
    except Exception as e:
        return None, None, str(e)

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_video_metadata(video_id: str, yt_api_key: str):
    title = ""
    desc = ""
    if yt_api_key:
        try:
            api_url = (
                f"https://www.googleapis.com/youtube/v3/videos"
                f"?part=snippet&id={urllib.parse.quote(video_id)}&key={urllib.parse.quote(yt_api_key)}"
            )
            r = requests.get(api_url, timeout=10)
            if r.status_code == 200:
                items = r.json().get("items", [])
                if items:
                    snip = items[0].get("snippet", {})
                    title = snip.get("title", "")
                    desc = snip.get("description", "")
        except Exception:
            pass

    if not title:
        try:
            watch_url = f"https://www.youtube.com/watch?v={video_id}"
            resp = requests.get(watch_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if resp.status_code == 200:
                m_title = re.search(r"<title>(.*?)</title>", resp.text, re.DOTALL)
                if m_title:
                    title = re.sub(r"\s*-\s*YouTube\s*$", "", m_title.group(1)).strip()
                m_desc = re.search(r'"shortDescription":"(.*?)"', resp.text)
                if m_desc:
                    desc = m_desc.group(1).encode("utf-8").decode("unicode_escape", errors="ignore")
        except Exception:
            pass

    return title, desc[:800]

def generate_fallback_script_with_ai(video_id: str, title: str, desc: str, gemini_key: str):
    topic_hint = f"Title: {title}\nDescription: {desc}" if (title or desc) else f"YouTube Video ID: {video_id}"
    prompt = (
        f"Based on this YouTube video context:\n{topic_hint}\n\n"
        f"Write a natural English spoken script/dialogue (about 120-180 words) with realistic vocabulary "
        f"matching the video topic so a learner can extract useful English words and collocations. "
        f"Return ONLY plain English text (no markdown headers or bullet lists)."
    )

    if gemini_key:
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_key}"
            list_res = requests.get(list_url, timeout=10)
            exclude_kw = ("exp", "thinking", "audio", "image", "tts", "vision", "embedding", "aqa")
            candidates = []
            if list_res.status_code == 200:
                for m in list_res.json().get("models", []):
                    m_name = m.get("name", "")
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        if "gemini" in m_name.lower() and not any(k in m_name.lower() for k in exclude_kw):
                            candidates.append(m_name)
            candidates.sort(key=lambda x: (0 if "flash" in x else 1, x))

            for model_path in candidates[:3]:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/{model_path}:generateContent?key={gemini_key}"
                    payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.5}}
                    res = requests.post(url, json=payload, timeout=18)
                    if res.status_code == 200:
                        txt = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                        if txt:
                            return txt
                except Exception:
                    continue
        except Exception:
            pass

    base_text = f"{title}. {desc}".strip(". ")
    if base_text:
        return base_text
    return "In this video, we explore key concepts, practical communication skills, and useful everyday expressions in English."

@st.cache_data(ttl=86400, show_spinner=False)
def translate_to_vi(text: str):
    try:
        return GoogleTranslator(source="en", target="vi").translate(text)
    except Exception:
        return ""

# --- CUSTOM CSS: WARM EDITORIAL VIDEO VOCAB ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.8rem;
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
        margin-bottom: 1.3rem;
    }

    .panel-card {
        background-color: #FFFFFF;
        border: 1px solid #E7E2D6;
        border-radius: 20px;
        padding: 18px 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 10px rgba(28, 25, 23, 0.02);
    }
    .panel-kicker {
        font-size: 0.72rem;
        font-weight: 800;
        color: #7C3AED;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .panel-heading {
        font-size: 1.12rem;
        font-weight: 800;
        color: #1C1917;
        margin-bottom: 10px;
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
        padding: 3px 10px;
        border-radius: 20px;
        margin-bottom: 10px;
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
    <div class="vid-sub">Video Transcript & Vocabulary Extractor</div>
    <div class="vid-title">YouTube Video Vocab</div>
    <div class="vid-desc">Dán link YouTube bất kỳ để bóc lời thoại (tự động dự phòng khi thiếu phụ đề CC), lọc từ vựng và lưu vào kho</div>
</div>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Vui lòng đăng nhập tại Dashboard trước!")
    st.stop()

username = st.session_state.username
yt_api_key = st.secrets.get("YOUTUBE_API_KEY", "").strip()
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
    analyze_clicked = st.button("Extract Script  ↗", type="primary", use_container_width=True)

segments = []
source_label = ""
video_id = extract_video_id(yt_url.strip()) if yt_url else None

if yt_url and not video_id:
    st.error("Link YouTube chưa đúng định dạng. Hãy kiểm tra lại đường dẫn nhé!")
    st.stop()

if video_id:
    with st.spinner("Đang trích xuất lời thoại từ video..."):
        cc_segments, mode_used, _ = fetch_youtube_transcript(video_id)

    if cc_segments:
        segments = cc_segments
        source_label = "Official / Auto Captions" if mode_used == "cc_en" else "Translated Captions -> EN"
    else:
        # Dự phòng tầng 2: lấy thông tin video + dựng lời thoại/nội dung sát chủ đề bằng AI
        v_title, v_desc = fetch_video_metadata(video_id, yt_api_key)
        fallback_text = generate_fallback_script_with_ai(video_id, v_title, v_desc, gemini_api_key)
        lines = [line.strip() for line in re.split(r"(?<=[.!?])\s+", fallback_text) if line.strip()]
        segments = [{"text": line, "start": i * 8} for i, line in enumerate(lines)]
        source_label = "AI Topic Script Fallback (No CC / Blocked)"

# Dự phòng tầng 3: cho phép dán lời thoại thủ công nếu muốn
with st.expander("Hoặc dán lời thoại / văn bản thủ công (áp dụng cho mọi video)", expanded=not bool(segments)):
    manual_script = st.text_area(
        "Dán lời thoại tiếng Anh vào đây nếu bạn muốn dùng bản script riêng:",
        placeholder="Paste English transcript or dialogue here...",
        height=110
    )
    if manual_script.strip():
        lines = [line.strip() for line in re.split(r"(?<=[.!?])\s+|\n+", manual_script.strip()) if line.strip()]
        segments = [{"text": line, "start": i * 6} for i, line in enumerate(lines)]
        source_label = "Custom Pasted Script"

if segments:
    full_text = " ".join(seg["text"].replace("\n", " ") for seg in segments)

    left_col, right_col = st.columns([1.15, 1], gap="large")

    with left_col:
        st.markdown('<div class="panel-card"><div class="panel-kicker">Source Player & Script</div>', unsafe_allow_html=True)
        if video_id:
            st.video(f"https://www.youtube.com/watch?v={video_id}")
        st.markdown(f'<span class="source-pill">{source_label}</span>', unsafe_allow_html=True)

        transcript_html = ""
        for seg in segments:
            mins = int(seg["start"] // 60)
            secs = int(seg["start"] % 60)
            t_str = f"{mins:02d}:{secs:02d}"
            clean_line = seg["text"].replace("\n", " ")
            transcript_html += f'<div style="margin-bottom:8px;"><span class="time-badge">{t_str}</span>{clean_line}</div>'

        st.markdown(f'<div class="transcript-box">{transcript_html}</div></div>', unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="panel-card"><div class="panel-kicker">Vocabulary Picker</div><div class="panel-heading">Nhặt từ vựng vào kho học</div>', unsafe_allow_html=True)

        raw_words = re.findall(r"\b[a-zA-Z]{5,}\b", full_text.lower())
        word_counts = Counter(w for w in raw_words if w not in STOPWORDS and w not in user_all_words)
        suggested_words = [w for w, _ in word_counts.most_common(40)]

        selected_from_list = st.multiselect(
            "1. Chọn từ hay hệ thống lọc được:",
            options=suggested_words,
            default=suggested_words[:3] if len(suggested_words) >= 3 else suggested_words
        )

        custom_phrase = st.text_input(
            "2. Hoặc nhập từ / cụm từ (Collocation) bạn thấy hay:",
            placeholder="e.g. take into account, sustainable..."
        )

        words_to_process = list(dict.fromkeys(
            selected_from_list + ([custom_phrase.strip().lower()] if custom_phrase.strip() else [])
        ))

        topic_name = st.text_input("Chủ đề lưu trong kho:", value="YouTube Video")

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
            st.info("Chọn từ ở danh sách trên hoặc nhập cụm từ bạn muốn lưu từ đoạn thoại bên trái.")

        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.info("Hãy dán một đường dẫn video YouTube vào ô phía trên hoặc mở phần dán lời thoại thủ công để bắt đầu.")
