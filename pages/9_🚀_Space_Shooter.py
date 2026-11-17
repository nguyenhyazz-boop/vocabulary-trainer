import json
import random
import streamlit as st
import streamlit.components.v1 as components
from utils.data_manager import load_data

st.set_page_config(page_title="Space Shooter | Vocabulary Trainer", page_icon="🚀", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 900px !important;
    }
    .app-title {
        font-size: 1.9rem !important;
        font-weight: 800 !important;
        color: #1E293B;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        text-align: center;
        color: #64748B;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="app-title">🚀 Space Vocab Defender</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Bắn hạ hạm đội tàu địch bằng cách gõ chính xác từ tiếng Anh tương ứng với nghĩa tiếng Việt!</div>', unsafe_allow_html=True)

# Kiểm tra đăng nhập
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Vui lòng đăng nhập tại Trang chủ trước!")
    st.stop()

username = st.session_state.username

# --- 1. TẢI DỮ LIỆU TỪ VỰNG CỦA USER ---
vocab_data = load_data(f"data_vocab_{username}.json")
colloc_data = load_data(f"data_collocation_{username}.json")

if not isinstance(vocab_data, dict): vocab_data = {}
if not isinstance(colloc_data, dict): colloc_data = {}

# --- 2. BẢNG THIẾT LẬP MÀN CHƠI ---
with st.expander("⚙️ Thiết lập đội hình & Chế độ chơi", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        source_choice = st.selectbox(
            "Nguồn từ vựng:",
            ["Normal Vocabulary", "Collocations & Phrases", "Tất cả từ đã lưu", "Chỉ từ hay sai (Wrong > 0)"]
        )
    with col2:
        game_mode = st.selectbox(
            "Chế độ hiển thị:",
            ["Thường (Có gợi ý khung chữ)", "Thử thách (Chỉ hiện nghĩa Việt)"]
        )
    with col3:
        difficulty = st.selectbox(
            "Tốc độ tàu địch:",
            ["Chậm (Khởi động)", "Trung bình (Chuẩn)", "Nhanh (Phản xạ cao)"]
        )

    # Lọc nguồn từ theo lựa chọn
    pool = {}
    if source_choice == "Normal Vocabulary":
        pool = vocab_data
    elif source_choice == "Collocations & Phrases":
        pool = colloc_data
    elif source_choice == "Tất cả từ đã lưu":
        pool = {**vocab_data, **colloc_data}
    else:
        combined = {**vocab_data, **colloc_data}
        pool = {k: v for k, v in combined.items() if isinstance(v, dict) and v.get("wrong", 0) > 0}

    all_keys = list(pool.keys())
    if not all_keys:
        st.info("Kho từ vựng bạn chọn hiện đang trống! Hãy thêm từ ở mục Library hoặc Add Word trước nhé.")
        st.stop()

    select_type = st.radio(
        "Cách chọn từ đưa vào trận:",
        ["Rút ngẫu nhiên theo số lượng", "Tự chọn từng từ muốn ôn"],
        horizontal=True
    )

    selected_words = []
    if select_type == "Rút ngẫu nhiên theo số lượng":
        num_words = st.slider("Số lượng tàu địch (từ vựng):", min_value=5, max_value=min(50, len(all_keys)), value=min(15, len(all_keys)))
        if st.button("🔄 Đổi bộ từ ngẫu nhiên khác"):
            st.session_state.space_seed = random.randint(1, 99999)
        seed = st.session_state.get("space_seed", 42)
        rng = random.Random(seed)
        selected_words = rng.sample(all_keys, num_words)
    else:
        selected_words = st.multiselect(
            "Chọn các từ bạn muốn đưa vào màn chơi:",
            options=all_keys,
            default=all_keys[:min(10, len(all_keys))]
        )

if not selected_words:
    st.warning("Vui lòng chọn ít nhất 1 từ vựng để bắt đầu!")
    st.stop()

# Chuẩn bị danh sách JSON truyền vào HTML5 Game
game_words = []
for w in selected_words:
    info = pool[w]
    meaning = info.get("meaning", str(info)) if isinstance(info, dict) else str(info)
    game_words.append({
        "en": w.strip(),
        "vi": meaning.strip()
    })

speed_map = {
    "Chậm (Khởi động)": 0.35,
    "Trung bình (Chuẩn)": 0.6,
    "Nhanh (Phản xạ cao)": 0.95
}
base_speed = speed_map[difficulty]
show_hint = "true" if "Thường" in game_mode else "false"
words_json = json.dumps(game_words, ensure_ascii=False)

# --- 3. GIAO DIỆN GAME VŨ TRỤ (HTML5 CANVAS + JS) ---
game_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; user-select: none; }}
  body {{
    background: #090D16;
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    color: #F8FAFC;
    display: flex;
    flex-direction: column;
    align-items: center;
  }}
  #game-wrapper {{
    position: relative;
    width: 100%;
    max-width: 840px;
    height: 580px;
    border-radius: 16px;
    overflow: hidden;
    border: 2px solid #1E293B;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5);
    background: radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%);
  }}
  canvas {{
    display: block;
    width: 100%;
    height: 100%;
  }}
  #hud {{
    position: absolute;
    top: 14px;
    left: 18px;
    right: 18px;
    display: flex;
    justify-content: space-between;
    pointer-events: none;
    font-size: 15px;
    font-weight: 700;
    z-index: 5;
  }}
  .hud-pill {{
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(56, 189, 248, 0.35);
    padding: 6px 14px;
    border-radius: 999px;
    backdrop-filter: blur(4px);
  }}
  #typing-bar {{
    position: absolute;
    bottom: 14px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid #38BDF8;
    border-radius: 10px;
    padding: 6px 18px;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #38BDF8;
    min-width: 220px;
    text-align: center;
    z-index: 5;
  }}
  .overlay {{
    position: absolute;
    inset: 0;
    background: rgba(9, 13, 22, 0.88);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    text-align: center;
    padding: 24px;
    z-index: 10;
  }}
  .overlay h2 {{
    font-size: 32px;
    margin-bottom: 10px;
    background: linear-gradient(90deg, #38BDF8, #818CF8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }}
  .overlay p {{
    color: #94A3B8;
    max-width: 480px;
    line-height: 1.5;
    margin-bottom: 22px;
  }}
  .btn-play {{
    background: linear-gradient(135deg, #0284C7, #4F46E5);
    color: white;
    border: none;
    padding: 14px 34px;
    font-size: 17px;
    font-weight: 700;
    border-radius: 12px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(56, 189, 248, 0.4);
    transition: transform 0.15s;
  }}
  .btn-play:hover {{ transform: scale(1.05); }}
  #missed-box {{
    margin-top: 14px;
    margin-bottom: 18px;
    max-height: 140px;
    overflow-y: auto;
    background: rgba(30, 41, 59, 0.7);
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 14px;
    color: #FCA5A5;
    text-align: left;
  }}
  #mobile-input {{
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }}
</style>
</head>
<body>

<div id="game-wrapper" onclick="focusInput()">
  <div id="hud">
    <div class="hud-pill">⭐ Điểm: <span id="score">0</span></div>
    <div class="hud-pill">🔥 Combo: <span id="combo">0</span></div>
    <div class="hud-pill">🛸 Còn lại: <span id="remaining">0</span></div>
    <div class="hud-pill">❤️ Giáp: <span id="lives">3</span></div>
  </div>

  <div id="typing-bar">Gõ phím để bắn...</div>
  <input id="mobile-input" type="text" autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false" />

  <div id="start-screen" class="overlay">
    <h2>SPACE VOCAB DEFENDER</h2>
    <p>Tàu địch mang <b>nghĩa tiếng Việt</b> đang tiến vào quỹ đạo.<br>
    Gõ chính xác <b>từ tiếng Anh</b> tương ứng trên bàn phím để phi thuyền bắn laser tiêu diệt!</p>
    <button class="btn-play" onclick="startGame()">🚀 XUẤT KÍCH NGAY</button>
  </div>

  <div id="end-screen" class="overlay" style="display: none;">
    <h2 id="end-title">HOÀN THÀNH NHIỆM VỤ!</h2>
    <p id="end-stats"></p>
    <div id="missed-box" style="display: none;"></div>
    <button class="btn-play" onclick="startGame()">🔄 CHƠI LẠI TRẬN NÀY</button>
  </div>

  <canvas id="gameCanvas" width="840" height="580"></canvas>
</div>

<script>
const WORD_LIST = {words_json};
const BASE_SPEED = {base_speed};
const SHOW_HINT = {show_hint};

const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");
const mobileInput = document.getElementById("mobile-input");

// Web Audio API tạo âm thanh laser & nổ không cần file ngoài
const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
function playSound(type) {{
  if (audioCtx.state === 'suspended') audioCtx.resume();
  const osc = audioCtx.createOscillator();
  const gain = audioCtx.createGain();
  osc.connect(gain);
  gain.connect(audioCtx.destination);

  const now = audioCtx.currentTime;
  if (type === 'laser') {{
    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(880, now);
    osc.frequency.exponentialRampToValueAtTime(220, now + 0.08);
    gain.gain.setValueAtTime(0.08, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
    osc.start(now);
    osc.stop(now + 0.08);
  }} else if (type === 'boom') {{
    osc.type = 'square';
    osc.frequency.setValueAtTime(140, now);
    osc.frequency.exponentialRampToValueAtTime(30, now + 0.25);
    gain.gain.setValueAtTime(0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
    osc.start(now);
    osc.stop(now + 0.25);
  }} else if (type === 'error') {{
    osc.type = 'triangle';
    osc.frequency.setValueAtTime(160, now);
    osc.frequency.linearRampToValueAtTime(110, now + 0.1);
    gain.gain.setValueAtTime(0.1, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);
    osc.start(now);
    osc.stop(now + 0.1);
  }}
}}

let stars = [];
for (let i = 0; i < 90; i++) {{
  stars.push({{
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 1.8 + 0.4,
    s: Math.random() * 0.4 + 0.1
  }});
}}

let enemies = [];
let lasers = [];
let particles = [];
let spawnQueue = [];
let lockedEnemy = null;
let score = 0;
let combo = 0;
let maxCombo = 0;
let lives = 3;
let isRunning = false;
let spawnTimer = 0;
let shipAngle = -Math.PI / 2;
let missedWords = [];
let correctChars = 0;
let totalChars = 0;

function focusInput() {{
  mobileInput.focus();
}}

function formatHint(word, typedCount) {{
  let out = "";
  for (let i = 0; i < word.length; i++) {{
    if (i < typedCount) {{
      out += word[i];
    }} else if (word[i] === " ") {{
      out += "   ";
    }} else if (word[i] === "-") {{
      out += "-";
    }} else if (SHOW_HINT && (i === 0 || i === word.length - 1)) {{
      out += word[i];
    }} else if (SHOW_HINT) {{
      out += "_";
    }} else {{
      out += "•";
    }}
    if (i < word.length - 1) out += " ";
  }}
  return out;
}}

function startGame() {{
  document.getElementById("start-screen").style.display = "none";
  document.getElementById("end-screen").style.display = "none";
  
  spawnQueue = [...WORD_LIST].sort(() => Math.random() - 0.5);
  enemies = [];
  lasers = [];
  particles = [];
  missedWords = [];
  lockedEnemy = null;
  score = 0;
  combo = 0;
  maxCombo = 0;
  lives = 3;
  correctChars = 0;
  totalChars = 0;
  spawnTimer = 999; // Spawn ngay lập tức con đầu tiên
  isRunning = true;
  
  updateHUD();
  document.getElementById("typing-bar").innerText = "Sẵn sàng khai hỏa...";
  focusInput();
  requestAnimationFrame(gameLoop);
}}

function spawnEnemy() {{
  if (spawnQueue.length === 0) return;
  const item = spawnQueue.pop();
  const margin = 120;
  const x = margin + Math.random() * (canvas.width - margin * 2);
  enemies.push({{
    en: item.en,
    enLower: item.en.toLowerCase(),
    vi: item.vi,
    typed: 0,
    x: x,
    y: -30,
    speed: BASE_SPEED + (Math.random() * 0.15)
  }});
}}

function createExplosion(x, y, color) {{
  for (let i = 0; i < 24; i++) {{
    const angle = Math.random() * Math.PI * 2;
    const speed = Math.random() * 4 + 1;
    particles.push({{
      x: x,
      y: y,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed,
      life: 1.0,
      color: color
    }});
  }}
}}

function updateHUD() {{
  document.getElementById("score").innerText = score;
  document.getElementById("combo").innerText = combo;
  document.getElementById("remaining").innerText = spawnQueue.length + enemies.length;
  document.getElementById("lives").innerText = "❤️".repeat(Math.max(0, lives));
}}

function handleKeyInput(char) {{
  if (!isRunning) return;
  const key = char.toLowerCase();
  if (!/^[a-z0-9\\s\\-']$/.test(key)) return;

  totalChars++;

  // Nếu chưa khóa mục tiêu, tìm tàu địch gần đáy nhất có chữ cái đầu khớp
  if (!lockedEnemy || !enemies.includes(lockedEnemy)) {{
    lockedEnemy = null;
    let candidates = enemies.filter(e => e.enLower[0] === key);
    if (candidates.length > 0) {{
      candidates.sort((a, b) => b.y - a.y);
      lockedEnemy = candidates[0];
    }}
  }}

  if (lockedEnemy) {{
    const expected = lockedEnemy.enLower[lockedEnemy.typed];
    if (key === expected) {{
      correctChars++;
      lockedEnemy.typed++;
      playSound('laser');

      // Bắn tia laser từ phi thuyền tới tàu địch
      const shipX = canvas.width / 2;
      const shipY = canvas.height - 65;
      shipAngle = Math.atan2(lockedEnemy.y - shipY, lockedEnemy.x - shipX);
      lasers.push({{ x1: shipX, y1: shipY, x2: lockedEnemy.x, y2: lockedEnemy.y, life: 1.0 }});
      createExplosion(lockedEnemy.x, lockedEnemy.y, "#38BDF8");

      const typedPart = lockedEnemy.en.slice(0, lockedEnemy.typed);
      document.getElementById("typing-bar").innerText = typedPart.toUpperCase();

      // Tiêu diệt hoàn toàn tàu địch
      if (lockedEnemy.typed >= lockedEnemy.en.length) {{
        playSound('boom');
        createExplosion(lockedEnemy.x, lockedEnemy.y, "#F59E0B");
        combo++;
        if (combo > maxCombo) maxCombo = combo;
        score += (lockedEnemy.en.length * 10) + (combo * 5);
        enemies = enemies.filter(e => e !== lockedEnemy);
        lockedEnemy = null;
        document.getElementById("typing-bar").innerText = "🎯 MỤC TIÊU BỊ HẠ!";
      }}
    }} else {{
      // Gõ sai chữ tiếp theo của tàu đang khóa
      combo = 0;
      playSound('error');
    }}
  }} else {{
    combo = 0;
    playSound('error');
  }}
  updateHUD();
}}

window.addEventListener("keydown", (e) => {{
  if (e.key === "Backspace") {{
    // Hủy khóa mục tiêu nếu muốn đổi sang bắn tàu khác
    lockedEnemy = null;
    document.getElementById("typing-bar").innerText = "Đã hủy khóa mục tiêu";
    return;
  }}
  if (e.key.length === 1) {{
    e.preventDefault();
    handleKeyInput(e.key);
  }}
}});

mobileInput.addEventListener("input", (e) => {{
  const val = mobileInput.value;
  if (val.length > 0) {{
    handleKeyInput(val[val.length - 1]);
    mobileInput.value = "";
  }}
}});

function endGame(isVictory) {{
  isRunning = false;
  const accuracy = totalChars > 0 ? Math.round((correctChars / totalChars) * 100) : 100;
  document.getElementById("end-title").innerText = isVictory ? "🏆 CHIẾN THẮNG TUYỆT ĐỐI!" : "💥 TÀU CHỦ BỊ PHÁ HỦY!";
  document.getElementById("end-stats").innerHTML = 
    `Điểm số: <b>${{score}}</b>  |  Max Combo: <b>${{maxCombo}}</b>  |  Độ chính xác: <b>${{accuracy}}%</b>`;

  const missedBox = document.getElementById("missed-box");
  if (missedWords.length > 0) {{
    missedBox.style.display = "block";
    missedBox.innerHTML = "<b>⚠️ Các từ để lọt cần ôn lại:</b><br>" + 
      missedWords.map(w => `• <b>${{w.en}}</b>: ${{w.vi}}`).join("<br>");
  }} else {{
    missedBox.style.display = "none";
  }}
  document.getElementById("end-screen").style.display = "flex";
}}

function gameLoop() {{
  if (!isRunning) return;

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Vẽ sao nền chuyển động
  ctx.fillStyle = "#FFFFFF";
  for (let s of stars) {{
    s.y += s.s;
    if (s.y > canvas.height) {{ s.y = 0; s.x = Math.random() * canvas.width; }}
    ctx.globalAlpha = 0.5;
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
    ctx.fill();
  }}
  ctx.globalAlpha = 1.0;

  // Sinh tàu địch mới
  spawnTimer++;
  const maxOnScreen = 4;
  if (spawnTimer > 150 && enemies.length < maxOnScreen && spawnQueue.length > 0) {{
    spawnEnemy();
    spawnTimer = 0;
  }}

  // Cập nhật & vẽ tàu địch
  for (let i = enemies.length - 1; i >= 0; i--) {{
    let e = enemies[i];
    e.y += e.speed;

    // Tàu chạm đáy màn hình
    if (e.y > canvas.height - 85) {{
      playSound('boom');
      createExplosion(e.x, e.y, "#EF4444");
      missedWords.push({{ en: e.en, vi: e.vi }});
      if (lockedEnemy === e) lockedEnemy = null;
      enemies.splice(i, 1);
      lives--;
      combo = 0;
      updateHUD();
      if (lives <= 0) {{
        endGame(false);
        return;
      }}
      continue;
    }}

    const isLocked = (lockedEnemy === e);

    // Vẽ thân tàu địch
    ctx.save();
    ctx.translate(e.x, e.y);
    ctx.fillStyle = isLocked ? "#F59E0B" : "#EF4444";
    ctx.beginPath();
    ctx.moveTo(0, 16);
    ctx.lineTo(-18, -10);
    ctx.lineTo(0, -4);
    ctx.lineTo(18, -10);
    ctx.closePath();
    ctx.fill();

    // Khung bảng nghĩa tiếng Việt + gợi ý chữ cái
    const hintText = formatHint(e.en, e.typed);
    ctx.font = "bold 15px 'Segoe UI', sans-serif";
    const viWidth = ctx.measureText(e.vi).width;
    ctx.font = "bold 14px monospace";
    const hintWidth = ctx.measureText(hintText).width;
    const boxW = Math.max(viWidth, hintWidth) + 26;
    const boxH = 46;

    ctx.fillStyle = isLocked ? "rgba(30, 41, 59, 0.95)" : "rgba(15, 23, 42, 0.85)";
    ctx.strokeStyle = isLocked ? "#F59E0B" : "#475569";
    ctx.lineWidth = isLocked ? 2 : 1;
    ctx.beginPath();
    ctx.roundRect(-boxW / 2, -62, boxW, boxH, 8);
    ctx.fill();
    ctx.stroke();

    // Text nghĩa tiếng Việt
    ctx.fillStyle = "#F8FAFC";
    ctx.font = "bold 14px 'Segoe UI', sans-serif";
    ctx.textAlign = "center";
    ctx.fillText(e.vi, 0, -43);

    // Text khung từ tiếng Anh
    ctx.fillStyle = isLocked ? "#38BDF8" : "#94A3B8";
    ctx.font = "bold 14px monospace";
    ctx.fillText(hintText, 0, -24);
    ctx.restore();
  }}

  // Vẽ tia laser
  for (let i = lasers.length - 1; i >= 0; i--) {{
    let l = lasers[i];
    ctx.strokeStyle = `rgba(56, 189, 248, ${{l.life}})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(l.x1, l.y1);
    ctx.lineTo(l.x2, l.y2);
    ctx.stroke();
    l.life -= 0.12;
    if (l.life <= 0) lasers.splice(i, 1);
  }}

  // Vẽ hạt nổ
  for (let i = particles.length - 1; i >= 0; i--) {{
    let p = particles[i];
    p.x += p.vx;
    p.y += p.vy;
    p.life -= 0.04;
    ctx.fillStyle = p.color;
    ctx.globalAlpha = Math.max(0, p.life);
    ctx.fillRect(p.x, p.y, 3, 3);
    if (p.life <= 0) particles.splice(i, 1);
  }}
  ctx.globalAlpha = 1.0;

  // Vẽ phi thuyền chủ ở đáy màn hình
  const shipX = canvas.width / 2;
  const shipY = canvas.height - 65;
  ctx.save();
  ctx.translate(shipX, shipY);
  ctx.rotate(shipAngle + Math.PI / 2);
  ctx.fillStyle = "#38BDF8";
  ctx.beginPath();
  ctx.moveTo(0, -22);
  ctx.lineTo(-16, 16);
  ctx.lineTo(0, 10);
  ctx.lineTo(16, 16);
  ctx.closePath();
  ctx.fill();
  ctx.restore();

  // Kiểm tra thắng trận
  if (spawnQueue.length === 0 && enemies.length === 0) {{
    endGame(true);
    return;
  }}

  requestAnimationFrame(gameLoop);
}}
</script>
</body>
</html>
"""

components.html(game_html, height=600)
