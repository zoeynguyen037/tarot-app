import streamlit as st
import anthropic
import random
from tarot_data import TAROT_CARDS

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Tarot by Zoey",
    page_icon="🔮",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
def init_state():
    defaults = {
        "step": "question",      # question | meditation | shuffle | pick | reading
        "question": "",
        "shuffled_deck": [],
        "reversed_map": {},
        "selected_ids": [],
        "reading_done": False,
        "reading_text": "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─────────────────────────────────────────────
# HANDLE QUERY PARAMS (from HTML pick component)
# ─────────────────────────────────────────────
params = st.query_params
if "picked" in params:
    raw   = params["picked"]
    parts = [x.strip() for x in raw.split(",") if x.strip().isdigit()]
    if len(parts) == 3:
        deck     = st.session_state.shuffled_deck
        selected = [deck[int(p)] for p in parts if int(p) < len(deck)]
        if len(selected) == 3:
            st.session_state.selected_ids = selected
            st.session_state.step = "reading"
    st.query_params.clear()
    st.rerun()

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def do_shuffle():
    deck = list(range(78))
    random.shuffle(deck)
    st.session_state.shuffled_deck   = deck
    st.session_state.reversed_map    = {i: (random.random() < 0.25) for i in range(78)}
    st.session_state.selected_ids    = []
    st.session_state.reading_done    = False
    st.session_state.reading_text    = ""

def get_client():
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        import os
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        st.error("⚠️ Chưa có API key. Thêm ANTHROPIC_API_KEY vào Streamlit secrets.")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

# ─────────────────────────────────────────────
# CSS — injected per screen
# ─────────────────────────────────────────────
def inject_css(step):
    cream = step in ("question", "meditation")
    bg    = "#EDE8DC" if cream else "#16141E"
    col   = "#2a2835" if cream else "#E8E4F5"
    btn_bg      = "linear-gradient(180deg,#ffffff 0%,#f3f1e8 100%)" if cream else "rgba(40,40,55,0.55)"
    btn_border  = "rgba(108,108,180,0.22)" if cream else "rgba(255,255,255,0.14)"
    btn_shadow  = "0 0 0 6px rgba(180,178,240,0.14),0 0 28px rgba(180,178,240,0.26),0 4px 12px rgba(0,0,0,0.06)" \
                  if cream else "0 0 22px rgba(197,203,245,0.15)"
    btn_hover   = "0 0 0 8px rgba(180,178,240,0.22),0 0 38px rgba(180,178,240,0.38)" \
                  if cream else "0 0 32px rgba(197,203,245,0.32)"
    ghost_col   = "rgba(108,108,180,0.6)"  if cream else "rgba(197,203,245,0.38)"
    back_col    = "rgba(42,40,53,0.38)"    if cream else "rgba(197,203,245,0.28)"
    ta_bg       = "rgba(255,255,255,0.55)" if cream else "rgba(255,255,255,0.05)"
    ta_border   = "rgba(108,108,180,0.18)" if cream else "rgba(197,203,245,0.12)"

    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600&family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;1,300;1,400;1,500&display=swap');

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.stApp {{
    background: {bg} !important;
    color: {col} !important;
}}
body, p, div, span, label, li {{
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    color: {col} !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}
.block-container {{
    padding-top: 1.4rem !important;
    padding-bottom: 2rem !important;
    max-width: 430px !important;
    margin: auto !important;
}}

/* ── Textarea ── */
textarea {{
    background: {ta_bg} !important;
    border: 1px solid {ta_border} !important;
    border-radius: 16px !important;
    color: {col} !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 17px !important;
    padding: 18px !important;
    resize: none !important;
    {'box-shadow: 0 4px 18px rgba(108,108,180,0.08), inset 0 0 0 1px rgba(255,255,255,0.4) !important;' if cream else ''}
}}
textarea:focus {{
    border-color: {'rgba(108,108,180,0.42)' if cream else 'rgba(197,203,245,0.28)'} !important;
    box-shadow: 0 0 0 3px {'rgba(180,178,240,0.16)' if cream else 'rgba(197,203,245,0.08)'} !important;
    outline: none !important;
}}

/* ── All buttons base ── */
.stButton > button {{
    width: 100% !important;
    border-radius: 999px !important;
    font-family: 'Cinzel', serif !important;
    font-size: 11.5px !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    border: 1px solid {btn_border} !important;
    background: {btn_bg} !important;
    color: {col} !important;
    padding: 15px 28px !important;
    backdrop-filter: blur(10px) !important;
    box-shadow: {btn_shadow} !important;
    transition: all 0.3s ease !important;
}}
.stButton > button:hover {{
    box-shadow: {btn_hover} !important;
    transform: translateY(-1px) !important;
    {'background: rgba(55,55,75,0.65) !important;' if not cream else ''}
}}

/* ── Prompt chip buttons ── */
div[data-testid="stHorizontalBlock"] .stButton > button,
.prompt-chip .stButton > button {{
    background: rgba(255,255,255,0.32) !important;
    border: 1px solid rgba(108,108,180,0.14) !important;
    border-radius: 12px !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-style: italic !important;
    font-size: 14px !important;
    letter-spacing: 0.01em !important;
    text-transform: none !important;
    color: #2a2835 !important;
    padding: 12px 16px !important;
    text-align: left !important;
    box-shadow: none !important;
}}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {{
    background: rgba(255,255,255,0.65) !important;
    transform: none !important;
    box-shadow: none !important;
}}

/* ── Ghost buttons ── */
.ghost-btn .stButton > button {{
    background: none !important;
    box-shadow: none !important;
    border: none !important;
    color: {ghost_col} !important;
    font-size: 10.5px !important;
    padding: 10px 20px !important;
    letter-spacing: 0.2em !important;
}}
.ghost-btn .stButton > button:hover {{
    transform: none !important;
    box-shadow: none !important;
}}

/* ── Back buttons ── */
.back-btn .stButton > button {{
    background: none !important;
    box-shadow: none !important;
    border: none !important;
    color: {back_col} !important;
    font-size: 10px !important;
    letter-spacing: 0.14em !important;
    padding: 8px 16px !important;
    width: auto !important;
}}
.back-btn .stButton > button:hover {{
    transform: none !important;
    box-shadow: none !important;
}}

/* ── Progress bar ── */
.stProgress > div > div {{
    background: linear-gradient(90deg, rgba(110,116,168,0.6), rgba(197,203,245,0.8)) !important;
    border-radius: 10px !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 3px; background: transparent; }}
::-webkit-scrollbar-thumb {{ background: rgba(180,178,240,0.18); border-radius: 3px; }}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SCREEN 1 — CÂU HỎI (cream)
# ─────────────────────────────────────────────
PROMPTS = [
    "Tình yêu của tôi sẽ đi về đâu?",
    "Tôi nên chọn con đường nào?",
    "Điều gì đang chờ đợi tôi trong công việc?",
    "Tôi cần buông bỏ điều gì?",
]

def screen_question():
    st.markdown("""
    <div style="text-align:center; padding:6px 0 20px;">
      <div style="font-family:'Cinzel',serif; font-size:10.5px; letter-spacing:0.28em;
                  text-transform:uppercase; color:rgba(108,108,180,0.55); margin-bottom:16px;">
        Tarot by Zoey
      </div>
      <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:15px;
                  line-height:1.65; color:rgba(42,40,53,0.55); max-width:290px; margin:auto;">
        Hãy đặt cho lá bài một câu hỏi rõ ràng.<br/>
        Câu hỏi càng cụ thể, lời đáp càng sâu sắc.
      </div>
    </div>
    """, unsafe_allow_html=True)

    question = st.text_area(
        label="",
        placeholder="Nhập câu hỏi của bạn…",
        height=128,
        key="q_input",
        label_visibility="collapsed",
    )

    # Suggested prompts label
    st.markdown("""
    <div style="font-family:'Cinzel',serif; font-size:9.5px; letter-spacing:0.22em;
                text-transform:uppercase; color:rgba(108,108,180,0.45);
                margin:14px 0 8px; text-align:center;">Gợi ý</div>
    """, unsafe_allow_html=True)

    # Prompt chips — full width stacked buttons
    for p in PROMPTS:
        if st.button(p, key=f"p_{p[:18]}"):
            st.session_state["q_input"] = p
            st.rerun()

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Tiếp tục", key="q_go", use_container_width=True):
            q = (question or "").strip()
            if not q:
                st.warning("Hãy nhập câu hỏi trước nhé.")
            else:
                st.session_state.question = q
                do_shuffle()
                st.session_state.step = "meditation"
                st.rerun()

# ─────────────────────────────────────────────
# SCREEN 2 — THIỀN ĐỊNH (cream)
# ─────────────────────────────────────────────
MEDITATION_HTML = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital@1&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{
    background:#EDE8DC; display:flex; flex-direction:column;
    align-items:center; justify-content:center; height:260px; overflow:hidden;
  }
  .orb{
    width:84px; height:84px; border-radius:50%;
    background:radial-gradient(circle at 40% 38%, #ffffff, #d8d6ee 45%, #a8a6c8 100%);
    box-shadow:0 0 40px rgba(168,166,200,0.45), 0 0 80px rgba(168,166,200,0.22);
    margin-bottom:28px;
    animation:drift 6s ease-in-out infinite;
  }
  @keyframes drift{0%,100%{transform:translateY(0) scale(1);}50%{transform:translateY(-10px) scale(1.04);}}
  p{
    font-family:'Cormorant Garamond',serif; font-style:italic;
    font-size:15px; line-height:1.68; text-align:center;
    color:rgba(42,40,53,0.62); max-width:280px;
  }
</style>
<div class="orb"></div>
<p>Trước khi đọc bài, hãy thanh lọc tâm trí.<br/>
Tập trung vào câu hỏi của bạn.<br/>
Hít thở sâu. Khi sẵn sàng, hãy tiếp tục.</p>
"""

def screen_meditation():
    q = st.session_state.question
    st.markdown(f"""
    <div style="text-align:center; padding:4px 0 10px;">
      <div style="font-family:'Cinzel',serif; font-size:10px; letter-spacing:0.26em;
                  text-transform:uppercase; color:rgba(108,108,180,0.45); margin-bottom:8px;">
        Đặt câu hỏi
      </div>
      <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:14.5px;
                  color:rgba(42,40,53,0.5); margin-bottom:0;">❝ {q} ❞</div>
    </div>
    """, unsafe_allow_html=True)

    st.components.v1.html(MEDITATION_HTML, height=260, scrolling=False)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Bắt đầu", key="med_go", use_container_width=True):
            st.session_state.step = "shuffle"
            st.rerun()

    st.markdown('<div class="ghost-btn">', unsafe_allow_html=True)
    g1, g2, g3 = st.columns([1, 2, 1])
    with g2:
        if st.button("Bỏ qua", key="med_skip", use_container_width=True):
            st.session_state.step = "shuffle"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SCREEN 3 — XÀO BÀI (dark)
# ─────────────────────────────────────────────
SHUFFLE_HTML = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400&family=Cormorant+Garamond:ital@1&display=swap');
  *{box-sizing:border-box;margin:0;padding:0;}
  body{
    background:#16141E; display:flex; flex-direction:column;
    align-items:center; justify-content:center; height:320px; overflow:hidden; position:relative;
  }
  .rays{position:absolute;inset:0;pointer-events:none;overflow:hidden;}
  .rays::before{
    content:''; position:absolute; top:50%; left:50%; width:500px; height:500px;
    background:conic-gradient(from 0deg,transparent 0deg,rgba(180,178,240,0.04) 1deg,
      transparent 3.5deg,transparent 7deg,rgba(180,178,240,0.03) 8.5deg,transparent 11deg);
    transform:translate(-50%,-50%); border-radius:50%;
    animation:spin 36s linear infinite;
  }
  @keyframes spin{to{transform:translate(-50%,-50%) rotate(360deg);}}

  .deck{position:relative; width:110px; height:176px; margin-bottom:24px; z-index:2;}
  .c{
    position:absolute; left:50%; top:50%;
    width:62px; height:99px; border-radius:8px;
    background:radial-gradient(ellipse at 50% 45%,#b8bee8 0%,#6e74a8 35%,#2a2c44 75%,#1a1a26 100%);
    box-shadow:0 4px 14px rgba(0,0,0,0.6),inset 0 0 12px rgba(0,0,0,0.32);
    transform:translate(-50%,-50%);
    display:flex; align-items:center; justify-content:center;
    border:1px solid rgba(110,116,168,0.35);
  }
  .c svg{width:66%; height:auto; opacity:0.5;}
  .c:nth-child(1){animation:s1 2.5s ease-in-out infinite;}
  .c:nth-child(2){animation:s2 2.5s ease-in-out infinite 0.1s;}
  .c:nth-child(3){animation:s3 2.5s ease-in-out infinite 0.2s;}
  .c:nth-child(4){animation:s4 2.5s ease-in-out infinite 0.3s;}
  .c:nth-child(5){animation:s5 2.5s ease-in-out infinite 0.4s;}
  .c:nth-child(6){animation:s6 2.5s ease-in-out infinite 0.5s;}
  .c:nth-child(7){animation:s7 2.5s ease-in-out infinite 0.6s;}

  @keyframes s1{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(calc(-50% - 42px),calc(-50% - 8px)) rotate(-20deg);}}
  @keyframes s2{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(calc(-50% - 24px),calc(-50% - 4px)) rotate(-11deg);}}
  @keyframes s3{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(calc(-50% - 10px),calc(-50% - 1px)) rotate(-4deg);}}
  @keyframes s4{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(-50%,-50%) rotate(1deg);}}
  @keyframes s5{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(calc(-50% + 10px),calc(-50% - 1px)) rotate(4deg);}}
  @keyframes s6{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(calc(-50% + 24px),calc(-50% - 4px)) rotate(11deg);}}
  @keyframes s7{0%,100%{transform:translate(-50%,-50%) rotate(0deg);}
    42%{transform:translate(calc(-50% + 42px),calc(-50% - 8px)) rotate(20deg);}}

  .lbl{
    font-family:'Cinzel',serif; font-size:10.5px; letter-spacing:0.28em;
    color:rgba(197,203,245,0.65); text-transform:uppercase; z-index:2;
    animation:pulse 3s ease-in-out infinite;
  }
  .sub{
    font-family:'Cormorant Garamond',serif; font-style:italic; font-size:14px;
    color:rgba(197,203,245,0.32); text-align:center; max-width:270px;
    z-index:2; line-height:1.55; margin-top:8px;
  }
  @keyframes pulse{0%,100%{opacity:0.55;}50%{opacity:1;}}
</style>
<div class="rays"></div>
<div class="deck">
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
  <div class="c"><svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(15,15,25,0.8)" stroke-width="0.7"/></svg></div>
</div>
<div class="lbl">Xáo bài</div>
<div class="sub">Giữ câu hỏi trong tâm trí.<br/>Khi cảm thấy đã đủ, hãy dừng lại.</div>
"""

def screen_shuffle():
    q = st.session_state.question
    st.markdown(f"""
    <div style="text-align:center; padding:4px 0 8px;">
      <div style="font-family:'Cinzel',serif; font-size:10px; letter-spacing:0.26em;
                  text-transform:uppercase; color:rgba(197,203,245,0.3); margin-bottom:6px;">
        Xáo bài
      </div>
      <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:14px;
                  color:rgba(197,203,245,0.32);">❝ {q} ❞</div>
    </div>
    """, unsafe_allow_html=True)

    st.components.v1.html(SHUFFLE_HTML, height=320, scrolling=False)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Đã đủ", key="shuf_done", use_container_width=True):
            st.session_state.step = "pick"
            st.rerun()

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 2, 1])
    with b2:
        if st.button("← Quay lại", key="shuf_back", use_container_width=True):
            st.session_state.step = "meditation"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SCREEN 4 — CHỌN BA LÁ (dark, HTML + form submit)
# ─────────────────────────────────────────────
PICK_HTML = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400&family=Cormorant+Garamond:ital,wght@1,400&display=swap');
*{box-sizing:border-box;margin:0;padding:0;}
html,body{height:100%;background:#16141E;color:#E8E4F5;overflow:hidden;}
body{display:flex;flex-direction:column;align-items:center;position:relative;}

.rays{position:absolute;inset:0;overflow:hidden;pointer-events:none;}
.rays::before{
  content:'';position:absolute;top:50%;left:50%;width:700px;height:700px;
  background:conic-gradient(from 0deg,transparent 0deg,rgba(180,178,240,0.03) 1deg,
    transparent 4deg,transparent 7.5deg,rgba(180,178,240,0.025) 9deg,transparent 12deg);
  transform:translate(-50%,-50%);animation:spin 42s linear infinite;border-radius:50%;
}
@keyframes spin{to{transform:translate(-50%,-50%) rotate(360deg);}}

.hd{
  position:relative;z-index:5;width:100%;padding:14px 20px 4px;
  text-align:center;
}
.title{font-family:'Cinzel',serif;font-size:10.5px;letter-spacing:0.26em;
       color:rgba(197,203,245,0.55);text-transform:uppercase;margin-bottom:5px;}
.sub{
  font-family:'Cormorant Garamond',serif;font-style:italic;
  font-size:14px;color:rgba(197,203,245,0.38);margin-bottom:3px;
}
.ctr{font-family:'Cinzel',serif;font-size:10px;color:rgba(197,203,245,0.3);
     letter-spacing:0.08em;margin-top:4px;}

.fan{
  position:relative;width:100%;height:220px;
  display:flex;justify-content:center;align-items:flex-end;
  flex-shrink:0;margin-top:6px;z-index:2;
}
.card-w{position:absolute;bottom:0;left:50%;transition:transform 0.55s cubic-bezier(0.7,0,0.3,1);}
.card{
  width:52px;height:83px;border-radius:7px;
  background:radial-gradient(ellipse at 50% 45%,#b8bee8 0%,#6e74a8 35%,#2a2c44 75%,#1a1a26 100%);
  box-shadow:0 4px 14px rgba(0,0,0,0.65),inset 0 0 10px rgba(0,0,0,0.3);
  cursor:pointer;
  display:flex;align-items:center;justify-content:center;
  border:1.5px solid rgba(110,116,168,0.38);
  transition:box-shadow 0.4s ease,border-color 0.4s ease;
  position:relative;
}
.card svg{width:62%;height:auto;opacity:0.48;}
.card.sel{
  box-shadow:0 0 20px rgba(197,203,245,0.7),0 0 42px rgba(197,203,245,0.28),0 4px 14px rgba(0,0,0,0.5);
  border-color:rgba(197,203,245,0.75);
}
.card.dis{opacity:0.3;cursor:default;}
.plbl{
  position:absolute;top:-18px;left:50%;transform:translateX(-50%);
  font-family:'Cinzel',serif;font-size:8.5px;letter-spacing:0.16em;
  color:rgba(197,203,245,0.85);text-transform:uppercase;white-space:nowrap;
}

.done-btn{
  display:none;margin-top:16px;padding:13px 44px;border-radius:999px;
  border:1px solid rgba(255,255,255,0.14);
  background:rgba(40,40,55,0.6);backdrop-filter:blur(10px);
  color:#E8E4F5;font-family:'Cinzel',serif;font-size:10.5px;letter-spacing:0.2em;
  text-transform:uppercase;cursor:pointer;
  box-shadow:0 0 22px rgba(197,203,245,0.18);
  transition:all 0.3s ease;position:relative;z-index:5;
}
.done-btn.show{display:block;}
.done-btn:hover{box-shadow:0 0 34px rgba(197,203,245,0.35);background:rgba(55,55,75,0.65);}
</style>
</head>
<body>
<form id="f" method="GET" target="_parent">
  <input type="hidden" name="picked" id="pickedVal">
</form>
<div class="rays"></div>
<div class="hd">
  <div class="title">Chọn ba lá</div>
  <div class="sub">Quá khứ · Hiện tại · Tương lai</div>
  <div class="ctr" id="ctr">Đã chọn 0 / 3</div>
</div>
<div class="fan" id="fan"></div>
<button class="done-btn" id="doneBtn" onclick="submit()">Xem kết quả →</button>

<script>
var N=13, MID=(N-1)/2;
var LBLS=['Quá khứ','Hiện tại','Tương lai'];
var picked=[];

function render(){
  var fan=document.getElementById('fan');
  fan.innerHTML='';
  for(var i=0;i<N;i++){
    var off=i-MID, angle=off*5.5, tx=off*16, ty=Math.abs(off)*4;
    var sel=picked.indexOf(i), isSel=sel!==-1, isDis=picked.length>=3&&!isSel;
    var w=document.createElement('div');
    w.className='card-w';
    w.style.transform='translate(-50%,0) translate('+tx+'px,'+(isSel?-112:ty)+'px) rotate('+(isSel?0:angle)+'deg)';
    w.style.zIndex=isSel?50+sel:i;
    var c=document.createElement('div');
    c.className='card'+(isSel?' sel':'')+(isDis?' dis':'');
    c.innerHTML='<svg viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/></svg>';
    if(isSel){var l=document.createElement('div');l.className='plbl';l.textContent=LBLS[sel];c.appendChild(l);}
    if(!isDis){(function(idx){c.onclick=function(){toggle(idx);};})(i);}
    w.appendChild(c);fan.appendChild(w);
  }
  document.getElementById('ctr').textContent='Đã chọn '+picked.length+' / 3';
  document.getElementById('doneBtn').className='done-btn'+(picked.length===3?' show':'');
}

function toggle(i){
  if(picked.includes(i)) picked=picked.filter(function(x){return x!==i;});
  else if(picked.length<3) picked.push(i);
  render();
}

function submit(){
  document.getElementById('pickedVal').value=picked.join(',');
  document.getElementById('f').submit();
}

render();
</script>
</body>
</html>"""

def screen_pick():
    st.components.v1.html(PICK_HTML, height=450, scrolling=False)

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 2, 1])
    with b2:
        if st.button("← Xào lại", key="pick_back", use_container_width=True):
            do_shuffle()
            st.session_state.step = "shuffle"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SCREEN 5 — ĐỌC BÀI (dark)
# ─────────────────────────────────────────────
POSITIONS = ["Quá Khứ", "Hiện Tại", "Tương Lai"]

def build_flip_html(cards_data):
    import json
    cards_json = []
    for card, is_rev in cards_data:
        cards_json.append({
            "name":    card["name"],
            "img":     card["image"],
            "rev":     is_rev,
            "summary": (card["reversed"] if is_rev else card["upright"])[:220] + "…",
        })
    data = json.dumps(cards_json, ensure_ascii=False)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500&family=Cormorant+Garamond:ital,wght@0,400;1,400&display=swap');
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{background:#16141E;color:#E8E4F5;font-family:'Cormorant Garamond',serif;overflow:hidden;}}
body{{display:flex;flex-direction:column;align-items:center;padding:10px 0 16px;}}

.pos-lbl{{
  font-family:'Cinzel',serif;font-size:10px;letter-spacing:0.26em;
  text-transform:uppercase;color:rgba(197,203,245,0.65);
  text-align:center;margin-bottom:8px;
}}
.flip-scene{{width:148px;height:236px;perspective:1200px;cursor:pointer;margin:0 auto;}}
.flip-card{{
  width:100%;height:100%;position:relative;
  transform-style:preserve-3d;
  transition:transform 0.9s cubic-bezier(0.7,0,0.3,1);
}}
.flip-card.flipped{{transform:rotateY(180deg);}}
.face,.back{{
  position:absolute;inset:0;backface-visibility:hidden;
  -webkit-backface-visibility:hidden;border-radius:10px;overflow:hidden;
}}
.face{{
  background:radial-gradient(ellipse at 50% 45%,#b8bee8 0%,#6e74a8 35%,#2a2c44 75%,#1a1a26 100%);
  display:flex;align-items:center;justify-content:center;
  box-shadow:0 8px 28px rgba(0,0,0,0.55);
  border:1.5px solid rgba(110,116,168,0.38);
}}
.face svg{{width:52%;height:auto;opacity:0.52;}}
.back{{transform:rotateY(180deg);background:#0d0b15;}}
.back img{{width:100%;height:100%;object-fit:cover;display:block;}}
.rev-badge{{
  position:absolute;top:7px;right:7px;z-index:2;
  background:rgba(170,55,85,0.75);backdrop-filter:blur(4px);
  color:#fff;font-family:'Cinzel',serif;font-size:7.5px;letter-spacing:0.12em;
  padding:3px 7px;border-radius:4px;text-transform:uppercase;
}}
.hint{{
  font-size:11px;color:rgba(197,203,245,0.28);font-style:italic;
  text-align:center;margin-top:7px;letter-spacing:0.03em;min-height:16px;
}}
.summary{{
  display:none;width:88%;margin:12px auto 0;
  background:rgba(36,34,54,0.65);backdrop-filter:blur(10px);
  border:1px solid rgba(255,255,255,0.07);border-radius:13px;
  padding:13px 15px;
}}
.summary.show{{display:block;animation:fu 0.4s ease;}}
@keyframes fu{{from{{opacity:0;transform:translateY(6px);}}to{{opacity:1;transform:translateY(0);}}}}
.sum-lbl{{font-family:'Cinzel',serif;font-size:8.5px;letter-spacing:0.2em;
          color:rgba(197,203,245,0.55);text-transform:uppercase;margin-bottom:5px;}}
.sum-txt{{font-size:13.5px;line-height:1.55;color:rgba(232,228,245,0.78);}}

.strip{{display:flex;gap:10px;margin-top:16px;justify-content:center;align-items:flex-end;}}
.thumb{{
  display:flex;flex-direction:column;align-items:center;gap:5px;
  cursor:pointer;opacity:0.38;transition:all 0.3s ease;
}}
.thumb.active{{opacity:1;transform:translateY(-3px) scale(1.06);}}
.tc{{
  width:36px;height:57px;border-radius:5px;
  background:radial-gradient(ellipse at 50% 45%,#b8bee8 0%,#6e74a8 35%,#2a2c44 75%,#1a1a26 100%);
  border:1px solid rgba(110,116,168,0.35);
  display:flex;align-items:center;justify-content:center;
  outline:1.5px solid transparent;outline-offset:3px;overflow:hidden;
  transition:outline 0.3s ease;
}}
.thumb.active .tc{{outline-color:rgba(232,235,255,0.6);}}
.tc img{{width:100%;height:100%;object-fit:cover;display:none;}}
.tc svg{{width:60%;height:auto;opacity:0.42;}}
.tlbl{{
  font-family:'Cinzel',serif;font-size:8px;letter-spacing:0.16em;
  text-transform:uppercase;color:rgba(197,203,245,0.38);
}}
.thumb.active .tlbl{{color:rgba(197,203,245,0.75);}}

.flip-btn{{
  margin-top:14px;padding:12px 38px;border-radius:999px;
  border:1px solid rgba(255,255,255,0.13);
  background:rgba(38,36,54,0.55);backdrop-filter:blur(10px);
  color:#E8E4F5;font-family:'Cinzel',serif;font-size:10.5px;
  letter-spacing:0.18em;text-transform:uppercase;cursor:pointer;
  box-shadow:0 0 18px rgba(197,203,245,0.16);transition:all 0.3s ease;
}}
.flip-btn:hover{{box-shadow:0 0 30px rgba(197,203,245,0.32);background:rgba(55,52,72,0.65);}}
.flip-btn.hidden{{display:none;}}
</style>
</head>
<body>
<script>
var C={data};
var POS=['Quá Khứ','Hiện Tại','Tương Lai'];
var focus=1, flipped=[false,false,false];

function render(){{
  var c=C[focus];
  document.getElementById('posLbl').textContent=POS[focus];
  var fc=document.getElementById('flipCard');
  flipped[focus]?fc.classList.add('flipped'):fc.classList.remove('flipped');
  document.getElementById('cardImg').src=c.img;
  document.getElementById('revBadge').style.display=c.rev?'block':'none';
  var sd=document.getElementById('summary');
  if(flipped[focus]){{
    sd.classList.add('show');
    document.getElementById('sumLbl').textContent=POS[focus]+' · '+c.name+(c.rev?' (ngược)':'');
    document.getElementById('sumTxt').textContent=c.summary;
  }}else sd.classList.remove('show');
  document.getElementById('hint').textContent=flipped[focus]?'':'Chạm để lật bài';
  document.getElementById('flipBtn').className='flip-btn'+(flipped[focus]?' hidden':'');
  for(var i=0;i<3;i++){{
    document.getElementById('th'+i).className='thumb'+(i===focus?' active':'');
    var ti=document.getElementById('ti'+i),ts=document.getElementById('ts'+i);
    if(flipped[i]){{ti.style.display='block';ti.src=C[i].img;ts.style.display='none';}}
    else{{ti.style.display='none';ts.style.display='block';}}
  }}
}}
function flip(){{flipped[focus]=!flipped[focus];render();}}
function go(i){{focus=i;render();}}
</script>

<div class="pos-lbl" id="posLbl">Hiện Tại</div>

<div class="flip-scene" onclick="flip()">
  <div class="flip-card" id="flipCard">
    <div class="face">
      <svg viewBox="0 0 60 96">
        <ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/>
        <ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/>
      </svg>
    </div>
    <div class="back">
      <img id="cardImg" src="" alt="">
      <div class="rev-badge" id="revBadge" style="display:none">↕ Ngược</div>
    </div>
  </div>
</div>
<div class="hint" id="hint">Chạm để lật bài</div>

<div class="summary" id="summary">
  <div class="sum-lbl" id="sumLbl"></div>
  <p class="sum-txt" id="sumTxt"></p>
</div>

<div class="strip">
  <div class="thumb" id="th0" onclick="go(0)">
    <div class="tc"><img id="ti0" src="" alt=""><svg id="ts0" viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/></svg></div>
    <div class="tlbl">Quá Khứ</div>
  </div>
  <div class="thumb active" id="th1" onclick="go(1)">
    <div class="tc"><img id="ti1" src="" alt=""><svg id="ts1" viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/></svg></div>
    <div class="tlbl">Hiện Tại</div>
  </div>
  <div class="thumb" id="th2" onclick="go(2)">
    <div class="tc"><img id="ti2" src="" alt=""><svg id="ts2" viewBox="0 0 60 96"><ellipse cx="23" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/><ellipse cx="37" cy="48" rx="12" ry="24" fill="none" stroke="rgba(12,12,22,0.8)" stroke-width="0.7"/></svg></div>
    <div class="tlbl">Tương Lai</div>
  </div>
</div>

<button class="flip-btn" id="flipBtn" onclick="flip()">Lật bài</button>
<script>render();</script>
</body>
</html>"""

def screen_reading():
    selected_ids = st.session_state.selected_ids
    reversed_map = st.session_state.reversed_map
    question     = st.session_state.question
    cards_data   = [(TAROT_CARDS[cid], reversed_map.get(cid, False)) for cid in selected_ids]

    st.markdown(f"""
    <div style="text-align:center; padding:4px 0 8px;">
      <div style="font-family:'Cinzel',serif; font-size:10px; letter-spacing:0.26em;
                  text-transform:uppercase; color:rgba(197,203,245,0.45);">Kết quả bói bài</div>
      <div style="font-family:'Cormorant Garamond',serif; font-style:italic; font-size:14px;
                  color:rgba(197,203,245,0.35); margin-top:5px;">❝ {question} ❞</div>
    </div>
    """, unsafe_allow_html=True)

    st.components.v1.html(build_flip_html(cards_data), height=510, scrolling=False)

    # Claude reading
    st.markdown("""
    <div style="text-align:center; margin:18px 0 8px;">
      <div style="font-family:'Cinzel',serif; font-size:9.5px; letter-spacing:0.24em;
                  text-transform:uppercase; color:rgba(197,203,245,0.4);">
        · · · Lời Giải Của Vũ Trụ · · ·
      </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.reading_done:
        spread_desc = ""
        for i, (card, is_rev) in enumerate(cards_data):
            spread_desc += (
                f"- {POSITIONS[i]}: **{card['name']}** ({card['english']}) — "
                f"{'ngược' if is_rev else 'xuôi'}\n"
                f"  Ý nghĩa: {card['reversed'] if is_rev else card['upright']}\n"
            )

        prompt = f"""Bạn là nhà chiêm tinh tarot với giọng văn ấm áp, sâu sắc và đầy trực giác.

Người dùng hỏi: "{question}"

Trải bài Quá Khứ – Hiện Tại – Tương Lai:
{spread_desc}

Viết đoạn giải bài hoàn chỉnh bằng tiếng Việt (~250 từ):
1. Kết nối 3 lá thành câu chuyện mạch lạc liên quan trực tiếp đến câu hỏi
2. Thông điệp cụ thể, thực tế
3. Giọng văn ấm áp, đồng cảm, không phán xét
4. Kết bằng lời khuyên ngắn và sâu sắc
5. KHÔNG giải thích lại ý nghĩa cơ bản của từng lá riêng lẻ"""

        client      = get_client()
        placeholder = st.empty()
        placeholder.markdown(
            '<div style="background:rgba(28,26,42,0.7);border:1px solid rgba(197,203,245,0.06);'
            'border-radius:14px;padding:15px 17px;font-style:italic;font-size:14px;'
            'color:rgba(197,203,245,0.3);">✦ Đang đọc bài cho bạn…</div>',
            unsafe_allow_html=True
        )
        full = ""
        try:
            with client.messages.stream(
                model="claude-opus-4-6",
                max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    full += text
                    placeholder.markdown(
                        f'<div style="background:rgba(28,26,42,0.7);border:1px solid rgba(197,203,245,0.06);'
                        f'border-radius:14px;padding:15px 17px;font-size:15px;line-height:1.72;'
                        f'color:rgba(232,228,245,0.82);">{full}▌</div>',
                        unsafe_allow_html=True
                    )
            placeholder.markdown(
                f'<div style="background:rgba(28,26,42,0.7);border:1px solid rgba(197,203,245,0.06);'
                f'border-radius:14px;padding:15px 17px;font-size:15px;line-height:1.72;'
                f'color:rgba(232,228,245,0.82);">{full}</div>',
                unsafe_allow_html=True
            )
            st.session_state.reading_done = True
            st.session_state.reading_text = full
        except Exception as e:
            placeholder.error(f"Lỗi API: {e}")
    else:
        st.markdown(
            f'<div style="background:rgba(28,26,42,0.7);border:1px solid rgba(197,203,245,0.06);'
            f'border-radius:14px;padding:15px 17px;font-size:15px;line-height:1.72;'
            f'color:rgba(232,228,245,0.82);">{st.session_state.reading_text}</div>',
            unsafe_allow_html=True
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Hỏi câu khác", key="new_q", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            init_state()
            st.rerun()
    with c2:
        if st.button("Xào lại", key="reshuf", use_container_width=True):
            do_shuffle()
            st.session_state.step = "shuffle"
            st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:22px;font-family:'Cormorant Garamond',serif;
                font-style:italic;font-size:12px;color:rgba(197,203,245,0.18);">
    Tarot là gương soi tâm hồn, không phải số phận bất biến.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────
step = st.session_state.get("step", "question")
inject_css(step)

if   step == "question":   screen_question()
elif step == "meditation": screen_meditation()
elif step == "shuffle":    screen_shuffle()
elif step == "pick":       screen_pick()
elif step == "reading":    screen_reading()
else:
    st.session_state.step = "question"
    st.rerun()
