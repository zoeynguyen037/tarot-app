import streamlit as st
import anthropic
from cards import CARD_OPTIONS

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Tarot Reading",
    page_icon="🔮",
    layout="centered",
)

# ── CUSTOM CSS — minimalist ───────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;1,300&family=Inter:wght@300;400&display=swap');

/* Background & base */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0e0e0e;
    color: #e8e0d5;
}
[data-testid="stHeader"] { background: transparent; }

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Typography */
h1 {
    font-family: 'Cormorant Garamond', serif;
    font-weight: 300;
    font-size: 2.6rem;
    letter-spacing: 0.12em;
    color: #e8e0d5;
    text-align: center;
    margin-bottom: 0.1rem;
}
.subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #7a7060;
    text-align: center;
    margin-bottom: 2.5rem;
}
label, .stSelectbox label, .stTextArea label {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #7a7060 !important;
}

/* Input fields */
textarea, .stSelectbox > div > div {
    background-color: #1a1a1a !important;
    border: 1px solid #2e2e2e !important;
    border-radius: 4px !important;
    color: #e8e0d5 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
}
textarea:focus, .stSelectbox > div > div:focus-within {
    border-color: #8b7355 !important;
    box-shadow: none !important;
}

/* Button */
.stButton > button {
    width: 100%;
    background: transparent;
    border: 1px solid #8b7355;
    color: #c4a882;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    padding: 0.75rem 1.5rem;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.25s ease;
    margin-top: 0.5rem;
}
.stButton > button:hover {
    background: #8b7355;
    color: #0e0e0e;
}
.stButton > button:active {
    transform: scale(0.99);
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #2e2e2e;
    margin: 2rem 0;
}

/* Card display row */
.card-row {
    display: flex;
    gap: 1.5rem;
    margin: 1.5rem 0;
}
.card-box {
    flex: 1;
    background: #141414;
    border: 1px solid #2e2e2e;
    border-radius: 4px;
    padding: 1.2rem 1rem;
    text-align: center;
}
.card-position {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7a7060;
    margin-bottom: 0.5rem;
}
.card-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    font-weight: 400;
    color: #c4a882;
}

/* Reading output */
.reading-box {
    background: #111111;
    border-left: 2px solid #8b7355;
    padding: 1.8rem 2rem;
    border-radius: 0 4px 4px 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.08rem;
    line-height: 1.85;
    color: #ddd5c8;
    white-space: pre-wrap;
}
.section-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #7a7060;
    margin: 1.8rem 0 0.6rem 0;
}

/* Spinner override */
[data-testid="stSpinner"] p {
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 0.15em;
    color: #7a7060;
}
</style>
""", unsafe_allow_html=True)


# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("<h1>🔮 Tarot</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Quá Khứ · Hiện Tại · Tương Lai</p>', unsafe_allow_html=True)

# ── API KEY ───────────────────────────────────────────────────────────────────
# Try secrets first, then session state input
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
    # Show selected cards
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

    # Build prompt
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

    # Reset button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ Xem bài khác"):
        st.rerun()
