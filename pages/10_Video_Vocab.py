import os
import re
import json
import time
import base64
import tempfile
import requests
from collections import Counter
import streamlit as st
import streamlit.components.v1 as components
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

def render_uploaded_player(file_bytes: bytes, mime_type: str):
    if not file_bytes:
        return
    if len(file_bytes) > 25 * 1024 * 1024:
        st.caption("File > 25MB — đã bóc băng thành công (ẩn trình phát preview để giữ trang mượt).")
        return
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    safe_mime = mime_type or "video/mp4"
    is_audio = safe_mime.startswith("audio/")
    tag_name = "audio" if is_audio else "video"
    media_style = (
        "width:100%;display:block;border-radius:10px;"
        if is_audio
        else "width:100%;max-height:245px;display:block;background:#1C1917;"
    )
    wrapper_style = (
        "padding:10px 12px;background:#FAF8F2;border-radius:14px;border:1px solid #E7E2D6;"
        if is_audio
        else "background:#1C1917;border-radius:14px;overflow:hidden;border:1px solid #E7E2D6;"
    )
    frame_h = 74 if is_audio else 255
    playsinline_attr = "" if is_audio else "playsinline"

    html_player = f"""
    <div style="{wrapper_style}">
        <{tag_name} controls {playsinline_attr} style="{media_style}">
            <source src="data:{safe_mime};base64,{b64}" type="{safe_mime}">
        </{tag_name}>
    </div>
    """
    components.html(html_player, height=frame_h)

@st.cache_data(ttl=3600, show_spinner=False)
def get_available_gemini_models(api_key: str) -> list:
    if not api_key:
        return []
    try:
        res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=12)
        if res.status_code == 200:
            exclude = ("exp", "thinking", "audio", "image", "tts", "vision", "embedding", "aqa", "1.0", "1.5")
            models = []
            for m in res.json().get("models", []):
                m_name = m.get("name", "")
                low = m_name.lower()
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods and "gemini" in low and not any(k in low for k in exclude):
                    models.append(m_name.replace("models/", ""))
            models.sort(key=lambda x: (0 if "2.5-flash" in x else (1 if "2.0-flash" in x else (2 if "flash" in x else 3)), x))
            if models:
                return models
    except Exception:
        pass
    return ["gemini-2.5-flash", "gemini-2.0-flash"]

@st.cache_data(ttl=7200, show_spinner=False)
def fetch_youtube_transcript(video_id: str):
    langs = ["en", "en-US", "en-GB", "en-CA", "en-AU"]
    try:
        if hasattr(YouTubeTranscriptApi, "fetch"):
            api = YouTubeTranscriptApi()
            try:
                t_list = api.fetch(video_id, languages=langs)
                segs = [{"text": s.text, "start": s.start} for s in t_list]
                if segs:
                    return segs, "YouTube CC · EN"
            except Exception:
                try:
                    transcript_list = api.list(video_id)
                    for tr in transcript_list:
                        if getattr(tr, "language_code", "").startswith("en"):
                            fetched = tr.fetch()
                            segs = [{"text": s.text, "start": s.start} for s in fetched]
                            if segs:
                                return segs, f"YouTube CC · {tr.language_code}"
                    for tr in transcript_list:
                        try:
                            trans = tr.translate("en").fetch()
                            segs = [{"text": s.text, "start": s.start} for s in trans]
                            if segs:
                                return segs, "Translated CC -> EN"
                        except Exception:
                            continue
                except Exception:
                    pass
        else:
            try:
                raw = YouTubeTranscriptApi.get_transcript(video_id, languages=langs)
                segs = [{"text": s["text"], "start": s["start"]} for s in raw]
                if segs:
                    return segs, "YouTube CC · EN"
            except Exception:
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    for tr in transcript_list:
                        try:
                            trans = tr.translate("en").fetch()
                            segs = [{"text": s["text"], "start": s["start"]} for s in trans]
                            if segs:
                                return segs, "Translated CC -> EN"
                        except Exception:
                            continue
                except Exception:
                    pass
    except Exception:
        pass
    return None, None

def upload_and_transcribe_file(file_path: str, mime_type: str, display_name: str, api_key: str):
    if not api_key:
        return None, "Chưa cấu hình GEMINI_API_KEY trong Secrets."
    if not file_path or not os.path.exists(file_path):
        return None, "Không tìm thấy file âm thanh/video tạm."

    file_size = os.path.getsize(file_path)
    if file_size <= 0:
        return None, "File rỗng."

    ext = os.path.splitext(file_path)[1].lower()
    ext_mime = {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".m4a": "audio/mp4",
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".ogg": "audio/ogg",
    }
    final_mime = ext_mime.get(ext, mime_type or "video/mp4")

    try:
        init_headers = {
            "X-Goog-Upload-Protocol": "resumable",
            "X-Goog-Upload-Command": "start",
            "X-Goog-Upload-Header-Content-Length": str(file_size),
            "X-Goog-Upload-Header-Content-Type": final_mime,
            "Content-Type": "application/json",
        }
        init_res = requests.post(
            f"https://generativelanguage.googleapis.com/upload/v1beta/files?key={api_key}",
            headers=init_headers,
            json={"file": {"display_name": display_name}},
            timeout=25
        )
        upload_url = (init_res.headers.get("X-Goog-Upload-URL") or "").strip()
        if not upload_url.startswith("http"):
            return None, f"Không lấy được URL upload từ Gemini ({init_res.status_code})."

        with open(file_path, "rb") as f_bin:
            up_res = requests.post(
                upload_url,
                headers={
                    "Content-Length": str(file_size),
                    "X-Goog-Upload-Offset": "0",
                    "X-Goog-Upload-Command": "upload, finalize",
                },
                data=f_bin,
                timeout=90
            )
        if up_res.status_code not in (200, 201):
            return None, f"Upload lỗi ({up_res.status_code}): {up_res.text[:180]}"

        file_info = up_res.json().get("file", {})
        file_uri = file_info.get("uri")
        file_name = file_info.get("name")
        if not file_uri or not file_name:
            return None, "Phản hồi upload thiếu thông tin file."

        for _ in range(20):
            st_res = requests.get(
                f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={api_key}",
                timeout=15
            )
            if st_res.status_code == 200:
                state = st_res.json().get("state")
                if state == "ACTIVE":
                    break
                if state == "FAILED":
                    return None, "Gemini xử lý file media thất bại."
            time.sleep(1.5)

        prompt = (
            "Listen carefully to this media file and transcribe ALL clear spoken English words or song lyrics. "
            "Keep timestamps accurate in seconds. Do NOT fabricate lyrics. "
            "Return ONLY a JSON array: [{\"start\": 0, \"text\": \"line\"}, ...]."
        )

        candidate_models = get_available_gemini_models(api_key)
        raw_out = ""
        last_err = ""

        for m_name in candidate_models:
            gen_res = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{m_name}:generateContent?key={api_key}",
                json={
                    "contents": [{
                        "parts": [
                            {"file_data": {"mime_type": final_mime, "file_uri": file_uri}},
                            {"text": prompt}
                        ]
                    }],
                    "generationConfig": {"temperature": 0.1}
                },
                timeout=90
            )
            if gen_res.status_code == 200:
                raw_out = gen_res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
                if raw_out:
                    break
            else:
                last_err = f"({gen_res.status_code}) {m_name}: {gen_res.text[:140]}"

        try:
            requests.delete(f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={api_key}", timeout=8)
        except Exception:
            pass

        if not raw_out:
            return None, f"Lỗi Gemini API {last_err}."

        m = re.search(r"\[.*\]", raw_out, re.DOTALL)
        if m:
            parsed = json.loads(m.group(0))
            segments = [
                {"start": float(item.get("start", i * 5)), "text": str(item.get("text", "")).strip()}
                for i, item in enumerate(parsed)
                if str(item.get("text", "")).strip()
            ]
            if segments:
                return segments, None

        lines = [ln.strip() for ln in raw_out.splitlines() if ln.strip() and not ln.startswith("```")]
        if lines:
            return [{"start": i * 5, "text": ln} for i, ln in enumerate(lines)], None

        return None, "Không nhận diện được lời thoại tiếng Anh rõ ràng trong file."
    except Exception as e:
        return None, f"Lỗi xử lý file: {e}"

@st.cache_data(ttl=86400, show_spinner=False)
def translate_words_batch_vi(words_tuple: tuple, gemini_key: str) -> dict:
    words_list = list(words_tuple)
    if not words_list:
        return {}
    result_map = {}
    if gemini_key:
        models = get_available_gemini_models(gemini_key)
        prompt = (
            f"Translate each English word or phrase in this list into concise Vietnamese meaning (1-4 words each). "
            f"Return ONLY valid JSON object mapping each exact word to its Vietnamese meaning:\n{json.dumps(words_list, ensure_ascii=False)}"
        )
        for m_name in models[:2]:
            try:
                res = requests.post(
                    f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){m_name}:generateContent?key={gemini_key}",
                    json={"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.2}},
                    timeout=15
                )
                if res.status_code == 200:
                    raw = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    m = re.search(r"\{.*\}", raw, re.DOTALL)
                    if m:
                        parsed = json.loads(m.group(0))
                        for k, v in parsed.items():
                            result_map[str(k).lower().strip()] = str(v).strip()
                        if result_map:
                            break
            except Exception:
                continue

    for w in words_list:
        wl = w.lower().strip()
        if not result_map.get(wl):
            try:
                from deep_translator import GoogleTranslator
                result_map[wl] = GoogleTranslator(source="en", target="vi").translate(w) or ""
            except Exception:
                result_map[wl] = ""
    return result_map

# --- CUSTOM CSS: WARM EDITORIAL & GỌN NÚT ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.8rem;
        max-width: 1020px !important;
    }

    .editorial-header {
        background: linear-gradient(135deg, #FAF8F2 0%, #F4F0E6 100%);
        border: 1px solid #E7E2D6;
        border-radius: 20px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .vid-kicker {
        display: inline-block;
        background-color: #EDE9FE;
        color: #7C3AED;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.85px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 999px;
        margin-bottom: 6px;
    }
    .vid-title {
        font-size: 1.9rem;
        font-weight: 800;
        color: #1C1917;
        letter-spacing: -0.5px;
        line-height: 1.15;
        margin: 0;
    }
    .vid-desc {
        color: #57534E;
        font-size: 0.93rem;
        margin-top: 5px;
        margin-bottom: 0;
    }

    /* Nút gọn gàng, đồng bộ Warm Editorial */
    .stButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        padding: 0.42rem 0.9rem !important;
        min-height: 2.35rem !important;
        transition: all 0.15s ease !important;
    }
    .stButton > button[kind="primary"] {
        background-color: #1C1917 !important;
        color: #FAF8F2 !important;
        border: 1px solid #1C1917 !important;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #332E2B !important;
        border-color: #332E2B !important;
    }
    .stButton > button[kind="secondary"] {
        background-color: #FAF8F2 !important;
        color: #1C1917 !important;
        border: 1px solid #DFD9C8 !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #EFECE3 !important;
        border-color: #C9C1AE !important;
    }

    .meta-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin: 10px 0 10px 0;
    }
    .source-pill {
        display: inline-flex;
        align-items: center;
        background-color: #EDE9FE;
        color: #5B21B6;
        font-size: 0.74rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 999px;
    }
    .saved-pill {
        display: inline-block;
        background-color: #FEF9C3;
        color: #854D0E;
        border: 1px solid #FDE047;
        font-size: 0.73rem;
        font-weight: 800;
        padding: 3px 9px;
        border-radius: 999px;
    }

    .transcript-box {
        background-color: #FAF8F2;
        border: 1px solid #E7E2D6;
        border-radius: 14px;
        padding: 14px 16px;
        max-height: 360px;
        overflow-y: auto;
        line-height: 1.72;
        font-size: 0.95rem;
        color: #1C1917;
    }
    .transcript-line {
        padding: 4px 0;
        border-bottom: 1px dashed #EAE5D9;
    }
    .transcript-line:last-child {
        border-bottom: none;
    }
    .time-badge {
        display: inline-block;
        background-color: #EDE9FE;
        color: #7C3AED;
        font-size: 0.73rem;
        font-weight: 800;
        padding: 1px 7px;
        border-radius: 6px;
        margin-right: 8px;
        font-family: monospace;
    }

    .word-chip-label {
        font-size: 0.94rem;
        font-weight: 700;
        color: #1C1917;
        padding-top: 6px;
    }

    span[data-baseweb="tag"] {
        background-color: #F6F3EB !important;
        color: #1C1917 !important;
        border: 1px solid #DFD9C8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] span { color: #1C1917 !important; }
    span[data-baseweb="tag"] svg { fill: #57534E !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="editorial-header">
    <div class="vid-kicker">Video & Audio Vocab</div>
    <h1 class="vid-title">YouTube Video Vocab</h1>
    <p class="vid-desc">Dán link YouTube lấy phụ đề nhanh (bị chặn thì bỏ qua), hoặc upload video/audio có âm thanh rõ để bóc lời và lưu từ vựng.</p>
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

for k, default_v in [
    ("vv_segments", []),
    ("vv_source", ""),
    ("vv_video_id", None),
    ("vv_skipped_link", False),
    ("vv_uploaded_bytes", b""),
    ("vv_uploaded_mime", ""),
]:
    if k not in st.session_state:
        st.session_state[k] = default_v

# --- 1. LINK YOUTUBE (BỊ CHẶN THÌ THÔI) ---
with st.container(border=True):
    st.caption("LINK YOUTUBE")
    col_url, col_btn = st.columns([4.3, 1.1], gap="small")
    with col_url:
        yt_url = st.text_input(
            "Link YouTube",
            placeholder="Dán link YouTube (vd: [https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)...)",
            label_visibility="collapsed"
        )
    with col_btn:
        extract_clicked = st.button("Lấy lời  ↗", type="primary", use_container_width=True)

parsed_vid = extract_video_id(yt_url.strip()) if yt_url else None
if yt_url and not parsed_vid:
    st.error("Link YouTube chưa đúng định dạng.")
    st.stop()

if parsed_vid and (extract_clicked or parsed_vid != st.session_state.vv_video_id):
    st.session_state.vv_video_id = parsed_vid
    st.session_state.vv_uploaded_bytes = b""
    st.session_state.vv_uploaded_mime = ""
    st.session_state.vv_skipped_link = False

    with st.spinner("Đang kiểm tra phụ đề..."):
        cc_segments, cc_mode = fetch_youtube_transcript(parsed_vid)

    if cc_segments:
        st.session_state.vv_segments = cc_segments
        st.session_state.vv_source = cc_mode
    else:
        st.session_state.vv_segments = []
        st.session_state.vv_source = ""
        st.session_state.vv_skipped_link = True

if st.session_state.vv_skipped_link and not st.session_state.vv_segments:
    st.info("Link này không lấy được phụ đề tự động — bỏ qua link và dùng phần upload video/audio có âm thanh rõ bên dưới nhé.")

# --- 2. UPLOAD VIDEO / AUDIO CÓ ÂM THANH RÕ ---
with st.container(border=True):
    st.caption("UPLOAD VIDEO / AUDIO")
    up_audio = st.file_uploader(
        "Chọn video hoặc audio có tiếng rõ (MP4, MP3, M4A, WAV, WEBM):",
        type=["mp4", "mp3", "m4a", "wav", "webm"],
        label_visibility="collapsed"
    )
    if up_audio is not None:
        c_act, c_hint = st.columns([1.4, 3.6], gap="small")
        with c_act:
            transcribe_clicked = st.button("Bóc lời ngay", type="primary", use_container_width=True)
        with c_hint:
            st.caption(f"File: {up_audio.name}")

        if transcribe_clicked:
            raw_bytes = up_audio.getvalue()
            ext = os.path.splitext(up_audio.name)[1].lower()
            ext_mime = {
                ".mp4": "video/mp4",
                ".webm": "video/webm",
                ".m4a": "audio/mp4",
                ".mp3": "audio/mpeg",
                ".wav": "audio/wav",
                ".ogg": "audio/ogg",
            }
            resolved_mime = ext_mime.get(ext, up_audio.type or "video/mp4")

            with st.spinner("Đang nghe âm thanh và bóc lời..."):
                with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".mp4") as tmp:
                    tmp.write(raw_bytes)
                    tmp_path = tmp.name
                try:
                    segs, up_err = upload_and_transcribe_file(
                        tmp_path,
                        resolved_mime,
                        up_audio.name,
                        gemini_api_key
                    )
                    if segs:
                        st.session_state.vv_segments = segs
                        st.session_state.vv_source = f"Audio/Video · {up_audio.name}"
                        st.session_state.vv_uploaded_bytes = raw_bytes
                        st.session_state.vv_uploaded_mime = resolved_mime
                        st.session_state.vv_skipped_link = False
                        st.rerun()
                    else:
                        st.error(up_err or "Không bóc được lời từ file này.")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

segments = st.session_state.vv_segments
source_label = st.session_state.vv_source
video_id = st.session_state.vv_video_id

# --- 3. TRÌNH PHÁT + TRANSCRIPT & NHẶT TỪ VỰNG ---
if segments:
    full_text = " ".join(seg["text"].replace("\n", " ") for seg in segments)
    left_col, right_col = st.columns([1.15, 1], gap="large")

    with left_col:
        with st.container(border=True):
            st.caption("MEDIA & SCRIPT")
            if st.session_state.vv_uploaded_bytes:
                render_uploaded_player(st.session_state.vv_uploaded_bytes, st.session_state.vv_uploaded_mime)
            elif video_id:
                components.iframe(f"[https://www.youtube.com/embed/](https://www.youtube.com/embed/){video_id}", height=240)

            if source_label:
                st.markdown(
                    f'<div class="meta-strip"><span class="source-pill">✦ {source_label}</span><span class="source-pill">{len(segments)} dòng</span></div>',
                    unsafe_allow_html=True
                )

            transcript_html = "".join(
                f'<div class="transcript-line"><span class="time-badge">{int(seg["start"] // 60):02d}:{int(seg["start"] % 60):02d}</span>{seg["text"].replace(chr(10), " ")}</div>'
                for seg in segments
            )
            st.markdown(f'<div class="transcript-box">{transcript_html}</div>', unsafe_allow_html=True)

    with right_col:
        with st.container(border=True):
            st.caption("VOCAB PICKER")
            st.markdown("#### Nhặt từ vào kho")

            raw_words = re.findall(r"\b[a-zA-Z]{4,}\b", full_text.lower())
            word_counts = Counter(w for w in raw_words if w not in STOPWORDS and w not in user_all_words)
            suggested_words = [w for w, _ in word_counts.most_common(40)]

            default_picks = suggested_words[:3] if len(suggested_words) >= 3 else suggested_words
            selected_from_list = st.multiselect(
                "Chọn từ gợi ý:",
                options=suggested_words,
                default=default_picks
            )

            custom_phrase = st.text_input(
                "Hoặc nhập từ / cụm từ hay:",
                placeholder="vd: take it easy, figure out..."
            )

            words_to_process = list(dict.fromkeys(
                selected_from_list + ([custom_phrase.strip().lower()] if custom_phrase.strip() else [])
            ))

            topic_name = st.text_input("Chủ đề:", value="Video Vocab")

            if words_to_process:
                st.divider()
                st.caption("NGHĨA TIẾNG VIỆT")
                vi_map = translate_words_batch_vi(tuple(words_to_process), gemini_api_key)

                for idx, w in enumerate(words_to_process):
                    auto_vi = vi_map.get(w.lower().strip(), "")
                    c1, c2, c3 = st.columns([1.2, 2.15, 0.95], gap="small")
                    with c1:
                        st.markdown(f'<div class="word-chip-label">{w}</div>', unsafe_allow_html=True)
                    with c2:
                        edited_vi = st.text_input(
                            f"Nghĩa của {w}",
                            value=auto_vi,
                            key=f"vi_{video_id or 'up'}_{w}_{idx}",
                            label_visibility="collapsed"
                        )
                    with c3:
                        if w in user_all_words:
                            st.markdown('<span class="saved-pill">Saved</span>', unsafe_allow_html=True)
                        else:
                            if st.button("Lưu", key=f"save_{video_id or 'up'}_{w}_{idx}", use_container_width=True):
                                is_phrase = " " in w.strip()
                                target_file = f"data_collocation_{username}.json" if is_phrase else f"data_vocab_{username}.json"
                                repo = load_data(target_file)
                                if not isinstance(repo, dict):
                                    repo = {}
                                repo[w] = {
                                    "meaning": edited_vi.strip() or auto_vi,
                                    "topic": topic_name.strip() or "Video Vocab",
                                    "correct": 0,
                                    "wrong": 0
                                }
                                save_data(repo, target_file)
                                st.toast(f"Đã lưu '{w}'")
                                st.rerun()
            else:
                st.info("Chọn từ hoặc nhập cụm từ để lưu.")
