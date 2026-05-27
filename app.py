import streamlit as st
import anthropic
from cards import CARD_OPTIONS

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tarot Reading",
    page_icon="🔮",
    layout="centered",
)

# ── CUSTOM CSS — light pastel ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Inter:wght@300;400&display=swap');

/* Background & base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #faf7f4;
    color: #3d3530;
}
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMain"] { background-color: #faf7f4; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Typography */
h1 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 300;
    font-size: 2.6rem;
    letter-spacing: 0.12em;
    color: #3d3530;
    text-align: center;
    margin-bottom: 0.1rem;
}
.subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #b09a93;
    text-align: center;
    margin-bottom: 2.5rem;
}
label, .stSelectbox label, .stTextArea label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: #b09a93 !important;
}

/* Input fields */
textarea {
    background-color: #ffffff !important;
    border: 1px solid #e8ddd8 !important;
    border-radius: 6px !important;
    color: #3d3530 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
}
textarea:focus {
    border-color: #c4a0a8 !important;
    box-shadow: 0 0 0 2px rgba(196,160,168,0.15) !important;
}
.stSelectbox > div > div {
    background-color: #ffffff !important;
    border: 1px solid #e8ddd8 !important;
    border-radius: 6px !important;
    color: #3d3530 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
}

/* Button */
.stButton > button {
    width: 100%;
    background: #c4a0a8;
    border: none;
    color: #ffffff;
    font-family: 'Inter', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    padding: 0.8rem 1.5rem;
    border-radius: 40px;
    cursor: pointer;
    transition: all 0.25s ease;
    margin-top: 0.5rem;
}
.stButton > button:hover {
    background: #b08a93;
    color: #ffffff;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(196,160,168,0.35);
}
.stButton > button:active {
    transform: translateY(0);
}
.stButton > button:disabled {
    background: #e8ddd8;
    color: #c0b0ac;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #edddd8;
    margin: 2rem 0;
}

/* Card display row */
.card-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.card-box {
    flex: 1;
    background: #ffffff;
    border: 1px solid #edddd8;
    border-radius: 12px;
    padding: 1.3rem 1rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(180,140,130,0.08);
}
.card-position {
    font-family: 'Inter', sans-serif;
    font-size: 0.62rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #b09a93;
    margin-bottom: 0.5rem;
}
.card-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.05rem;
    font-weight: 400;
    color: #8a5f68;
}

/* Reading output */
.reading-box {
    background: #ffffff;
    border: 1px solid #edddd8;
    border-left: 3px solid #c4a0a8;
    padding: 2rem 2.2rem;
    border-radius: 0 12px 12px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    line-height: 1.9;
    color: #4a3c38;
    white-space: pre-wrap;
    box-shadow: 0 2px 12px rgba(180,140,130,0.08);
}
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #b09a93;
    margin: 1.8rem 0 0.6rem 0;
}

/* Spinner */
[data-testid="stSpinner"] p {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    color: #b09a93;
}
</style>
""", unsafe_allow_html=True)


# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("<h1>🔮 Tarot</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Quá Khứ · Hiện Tại · Tương Lai</p>', unsafe_allow_html=True)

# ── API KEY ───────────────────────────────────────────────────────────────────
api_key = st.secrets.get("ANTHROPIC_API_KEY", "") if hasattr(st, "secrets") else ""
if not api_key:
    api_key = st.session_state.get("api_key", "")

if not api_key:
    with st.expander("⚙️ Cài đặt API Key", expanded=True):
        key_input = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
            help="API key sẽ không được lưu lại sau khi đóng tab",
        )
        if key_input:
            st.session_state["api_key"] = key_input
            api_key = key_input
            st.rerun()

st.markdown("<hr>", unsafe_allow_html=True)

# ── QUESTION INPUT ────────────────────────────────────────────────────────────
question = st.text_area(
    "Câu hỏi của bạn",
    placeholder="Bạn muốn tìm hướng về vấn đề gì? (công việc, tình yêu, quyết định...)",
    height=90,
    max_chars=500,
)

# ── CARD SELECTORS ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<p class="section-label">🔙 Quá khứ</p>', unsafe_allow_html=True)
    card1 = st.selectbox("Lá 1", ["— chọn lá —"] + CARD_OPTIONS, label_visibility="collapsed", key="c1")

with col2:
    st.markdown('<p class="section-label">🎯 Hiện tại</p>', unsafe_allow_html=True)
    card2 = st.selectbox("Lá 2", ["— chọn lá —"] + CARD_OPTIONS, label_visibility="collapsed", key="c2")

with col3:
    st.markdown('<p class="section-label">🔮 Tương lai</p>', unsafe_allow_html=True)
    card3 = st.selectbox("Lá 3", ["— chọn lá —"] + CARD_OPTIONS, label_visibility="collapsed", key="c3")

# ── VALIDATE & READ ───────────────────────────────────────────────────────────
cards_selected = all(c != "— chọn lá —" for c in [card1, card2, card3])
ready = api_key and question.strip() and cards_selected

st.markdown("<br>", unsafe_allow_html=True)
read_btn = st.button("✦ Xem Bài", disabled=not ready)

if not ready and (question or cards_selected):
    missing = []
    if not api_key:
        missing.append("API key")
    if not question.strip():
        missing.append("câu hỏi")
    if not cards_selected:
        missing.append("đủ 3 lá bài")
    st.caption(f"Cần có: {', '.join(missing)}")

# ── READING ───────────────────────────────────────────────────────────────────
if read_btn and ready:
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class="card-row">
        <div class="card-box">
            <div class="card-position">🔙 Quá khứ</div>
            <div class="card-name">{card1.split(' (')[0]}</div>
        </div>
        <div class="card-box">
            <div class="card-position">🎯 Hiện tại</div>
            <div class="card-name">{card2.split(' (')[0]}</div>
        </div>
        <div class="card-box">
            <div class="card-position">🔮 Tương lai</div>
            <div class="card-name">{card3.split(' (')[0]}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    system_prompt = """Bạn là người đọc bài Tarot theo phong cách tâm lý học — không bói toán, không phán xét, không dùng ngôn ngữ huyền bí cứng nhắc. Bạn đọc bài như một người bạn thông minh, empathetic, giúp người đọc tự nhìn lại mình.

Phong cách viết:
- Tiếng Việt tự nhiên, gần gũi, dễ hiểu — không dùng từ hoa mỹ quá mức
- Đủ dài và chi tiết để có chiều sâu, nhưng không lan man
- Mỗi lá bài được đọc theo vị trí của nó, rồi KẾT NỐI thành một câu chuyện xuyên suốt — lá trước làm nền cho lá sau
- Không đọc từng lá một cách rời rạc; hãy dệt chúng thành một narrative liên mạch
- Kết thúc bằng 1 câu hỏi gợi mở để người đọc tự suy ngẫm (không phải lời tiên tri)
- Không dùng bullet points — viết thành đoạn văn

Cấu trúc:
1. Đọc Lá 1 (Quá khứ) — bối cảnh/nguồn gốc
2. Đọc Lá 2 (Hiện tại) — kết nối từ lá 1, mô tả năng lượng đang diễn ra
3. Đọc Lá 3 (Tương lai) — xu hướng nếu tiếp tục pattern hiện tại
4. Tóm lại — kết nối cả 3 lá thành một câu chuyện, kết thúc bằng câu hỏi suy ngẫm"""

    user_prompt = f"""Câu hỏi: {question.strip()}

Trải bài 3 lá:
- Quá khứ: {card1}
- Hiện tại: {card2}
- Tương lai: {card3}

Hãy đọc bài cho tôi."""

    with st.spinner("Đang đọc bài..."):
        try:
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-opus-4-6",
                max_tokens=1200,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            reading = response.content[0].text

            st.markdown('<p class="section-label">✦ Bài Đọc</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="reading-box">{reading}</div>', unsafe_allow_html=True)

        except anthropic.AuthenticationError:
            st.error("API key không hợp lệ. Vui lòng kiểm tra lại.")
        except anthropic.RateLimitError:
            st.error("Đã đạt giới hạn API. Vui lòng thử lại sau.")
        except Exception as e:
            st.error(f"Có lỗi xảy ra: {str(e)}")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ Xem bài khác"):
        st.rerun()
