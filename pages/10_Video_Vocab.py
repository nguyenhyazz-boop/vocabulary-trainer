import os
import re
import json
import time
import tempfile
import requests
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

def get_best_gemini_model(api_key: str) -> str:
    try:
        res = requests.get(f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}", timeout=10)
        if res.status_code == 200:
            exclude = ("exp", "thinking", "audio", "image", "tts", "vision", "embedding", "aqa")
            models = [
                m["name"].replace("models/", "")
                for m in res.json().get("models", [])
                if "generateContent" in m.get("supportedGenerationMethods", [])
                and "gemini" in m.get("name", "").lower()
                and not any(k in m.get("name", "").lower() for k in exclude)
            ]
            models.sort(key=lambda x: (0 if "flash" in x else 1, x))
            if models:
                return models[0]
    except Exception:
        pass
    return "gemini-2.5-flash"

@st.cache_data(ttl=3600, show_spinner=False)
def fetch_youtube_transcript(video_id: str):
    try:
        if hasattr(YouTubeTranscriptApi, "fetch"):
            api = YouTubeTranscriptApi()
            try:
                t_list = api.fetch(video_id, languages=["en", "en-US", "en-GB"])
                segs = [{"text": s.text, "start": s.start} for s in t_list]
                if segs:
                    return segs, "Official / Auto Captions"
            except Exception:
                for tr in api.list(video_id):
                    try:
                        trans = tr.translate("en").fetch()
                        segs = [{"text": s.text, "start": s.start} for s in trans]
                        if segs:
                            return segs, "Translated Captions -> EN"
                    except Exception:
                        continue
        else:
            try:
                raw = YouTubeTranscriptApi.get_transcript(video_id, languages=["en", "en-US", "en-GB"])
                segs = [{"text": s["text"], "start": s["start"]} for s in raw]
                if segs:
                    return segs, "Official / Auto Captions"
            except Exception:
                for tr in YouTubeTranscriptApi.list_transcripts(video_id):
                    try:
                        trans = tr.translate("en").fetch()
                        segs = [{"text": s["text"], "start": s["start"]} for s in trans]
                        if segs:
                            return segs, "Translated Captions -> EN"
                    except Exception:
                        continue
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
            return None, f"Không lấy được URL upload ({init_res.status_code})."

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

        # Chờ Gemini xử lý xong file media trước khi gọi generateContent
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
            "Listen carefully to this media file and transcribe ALL spoken words or song lyrics into English. "
            "Do NOT make up unrelated content. "
            "Return ONLY a JSON array: [{\"start\": 0, \"text\": \"line\"}, ...]."
        )

        candidate_models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
        best_model = get_best_gemini_model(api_key)
        if best_model not in candidate_models:
            candidate_models.insert(0, best_model)

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
                last_err = f"({gen_res.status_code}) {gen_res.text[:160]}"

        try:
            requests.delete(f"https://generativelanguage.googleapis.com/v1beta/{file_name}?key={api_key}", timeout=8)
        except Exception:
            pass

        if not raw_out:
            return None, f"Lỗi Gemini API {last_err or '(404)'}."

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

        return None, "Không nhận diện được lời thoại tiếng Anh trong file."
    except Exception as e:
        return None, f"Lỗi xử lý file: {e}"

@st.cache_data(ttl=3600, show_spinner=False)
def transcribe_youtube_audio(video_id: str, api_key: str):
    try:
        import yt_dlp
    except ImportError:
        return None, "Thiếu thư viện yt-dlp trong requirements.txt."

    url = f"[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=){video_id}"
    with tempfile.TemporaryDirectory() as tmpdir:
        out_tpl = os.path.join(tmpdir, "audio.%(ext)s")
        ydl_opts = {
            "format": "worstaudio[ext=m4a]/worstaudio/bestaudio",
            "outtmpl": out_tpl,
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "max_filesize": 25 * 1024 * 1024,
            "extractor_args": {
                "youtube": {
                    "player_client": ["android", "ios", "web"]
                }
            }
        }

        audio_path = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            for f in os.listdir(tmpdir):
                if f.startswith("audio."):
                    audio_path = os.path.join(tmpdir, f)
                    break
        except Exception as e:
            return None, f"YouTube chặn tải luồng audio từ IP Cloud ({e})."

        if not audio_path or not os.path.exists(audio_path):
            return None, "Không tải được luồng âm thanh của video này trên server Cloud."

        ext = os.path.splitext(audio_path)[1].lower()
        mime_map = {".m4a": "audio/mp4", ".mp3": "audio/mp3", ".webm": "audio/webm", ".ogg": "audio/ogg", ".opus": "audio/opus"}
        return upload_and_transcribe_file(audio_path, mime_map.get(ext, "audio/mp4"), f"yt_{video_id}", api_key)

@st.cache_data(ttl=86400, show_spinner=False)
def translate_words_batch_vi(words_tuple: tuple, gemini_key: str) -> dict:
    words_list = list(words_tuple)
    if not words_list:
        return {}
    result_map = {}
    if gemini_key:
        model_name = get_best_gemini_model(gemini_key)
        prompt = (
            f"Translate each English word or phrase in this list into concise Vietnamese meaning (1-4 words each). "
            f"Return ONLY valid JSON object mapping each exact word to its Vietnamese meaning:\n{json.dumps(words_list, ensure_ascii=False)}"
        )
        try:
            res = requests.post(
                f"[https://generativelanguage.googleapis.com/v1beta/models/](https://generativelanguage.googleapis.com/v1beta/models/){model_name}:generateContent?key={gemini_key}",
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
        max-height: 360px;
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
    span[data-baseweb="tag"] span { color: #1C1917 !important; }
    span[data-baseweb="tag"] svg { fill: #57534E !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div>
    <div class="vid-sub">AI Audio & Caption Transcriber</div>
    <div class="vid-title">YouTube Video Vocab</div>
    <div class="vid-desc">Tự động lấy phụ đề CC, bóc băng từ âm thanh video hoặc tải file audio / dán lời thủ công</div>
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

for k, default_v in [("vv_segments", []), ("vv_source", ""), ("vv_video_id", None), ("vv_error", "")]:
    if k not in st.session_state:
        st.session_state[k] = default_v

col_url, col_btn = st.columns([4, 1.2], gap="small")
with col_url:
    yt_url = st.text_input(
        "Link YouTube",
        placeholder="Paste YouTube link (e.g. [https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=)...)",
        label_visibility="collapsed"
    )
with col_btn:
    extract_clicked = st.button("Extract Script  ↗", type="primary", use_container_width=True)

parsed_vid = extract_video_id(yt_url.strip()) if yt_url else None
if yt_url and not parsed_vid:
    st.error("Link YouTube chưa đúng định dạng. Hãy kiểm tra lại đường dẫn nhé!")
    st.stop()

if parsed_vid and (extract_clicked or parsed_vid != st.session_state.vv_video_id):
    st.session_state.vv_video_id = parsed_vid
    st.session_state.vv_error = ""

    with st.spinner("Bước 1/2: Đang kiểm tra phụ đề CC..."):
        cc_segments, cc_mode = fetch_youtube_transcript(parsed_vid)

    if cc_segments:
        st.session_state.vv_segments = cc_segments
        st.session_state.vv_source = cc_mode
    else:
        with st.spinner("Bước 2/2: Đang thử tách âm thanh & bóc băng bằng Gemini AI..."):
            ai_segments, ai_err = transcribe_youtube_audio(parsed_vid, gemini_api_key)
        if ai_segments:
            st.session_state.vv_segments = ai_segments
            st.session_state.vv_source = "Gemini AI Audio Transcription"
        else:
            st.session_state.vv_segments = []
            st.session_state.vv_source = ""
            st.session_state.vv_error = ai_err or "Không thể tự bóc từ link này trên Cloud."

if st.session_state.vv_error:
    st.warning(f"Lưu ý: {st.session_state.vv_error}")

with st.expander("Tải file audio/video lên (MP3, M4A, MP4) hoặc dán lời thủ công", expanded=bool(st.session_state.vv_error)):
    up_audio = st.file_uploader("Upload file audio/video để Gemini bóc băng:", type=["mp3", "m4a", "wav", "mp4", "webm"])
    if up_audio is not None and st.button("Bóc băng từ file đã tải lên", type="primary"):
        with st.spinner("Gemini AI đang nghe và chép lời từ file của bạn..."):
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(up_audio.name)[1]) as tmp:
                tmp.write(up_audio.read())
                tmp_path = tmp.name
            try:
                segs, up_err = upload_and_transcribe_file(
                    tmp_path,
                    up_audio.type or "audio/mp4",
                    up_audio.name,
                    gemini_api_key
                )
                if segs:
                    st.session_state.vv_segments = segs
                    st.session_state.vv_source = f"Uploaded File: {up_audio.name}"
                    st.session_state.vv_error = ""
                    st.rerun()
                else:
                    st.error(up_err or "Không thể bóc băng file này.")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

    manual_script = st.text_area("Hoặc dán trực tiếp lời bài hát / lời thoại tiếng Anh:", height=110)
    if manual_script.strip():
        lines = [line.strip() for line in re.split(r"\n+", manual_script.strip()) if line.strip()]
        st.session_state.vv_segments = [{"text": line, "start": i * 5} for i, line in enumerate(lines)]
        st.session_state.vv_source = "Manual Transcript"
        st.session_state.vv_error = ""

segments = st.session_state.vv_segments
source_label = st.session_state.vv_source
video_id = st.session_state.vv_video_id

if segments:
    full_text = " ".join(seg["text"].replace("\n", " ") for seg in segments)
    left_col, right_col = st.columns([1.15, 1], gap="large")

    with left_col:
        with st.container(border=True):
            st.caption("SOURCE PLAYER & SCRIPT")
            if video_id:
                st.video(f"[https://www.youtube.com/watch?v=](https://www.youtube.com/watch?v=){video_id}")
            if source_label:
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
                st.caption("Nghĩa tiếng Việt tự động dịch:")
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
                st.info("Chọn từ ở danh sách trên hoặc nhập cụm từ bạn muốn lưu.")
else:
    st.info("Dán link YouTube để hệ thống tự động lấy CC hoặc bóc băng.")
