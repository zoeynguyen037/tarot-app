# 🔮 Bói Bài Tarot — Streamlit App

App bói bài Tarot tiếng Việt với AI giải bài, deploy lên Streamlit Cloud.

---

## 📁 Cấu trúc file

```
tarot-app/
├── app.py                  ← App chính
├── tarot_data.py           ← Data 78 lá bài tiếng Việt
├── requirements.txt        ← Dependencies
├── .streamlit/
│   └── config.toml         ← Theme dark mystical
└── README.md
```

---

## 🚀 Deploy lên Streamlit Cloud (từng bước)

### Bước 1 — Tạo GitHub repo

1. Vào [github.com](https://github.com) → **New repository**
2. Đặt tên ví dụ: `tarot-app`
3. Chọn **Public**
4. Nhấn **Create repository**

### Bước 2 — Upload files

Kéo thả tất cả files vào GitHub:
- `app.py`
- `tarot_data.py`
- `requirements.txt`
- `.streamlit/config.toml` *(tạo folder `.streamlit` rồi upload)*

### Bước 3 — Lấy Anthropic API Key

1. Vào [console.anthropic.com](https://console.anthropic.com)
2. Vào **API Keys** → **Create Key**
3. Copy key (bắt đầu bằng `sk-ant-...`)

### Bước 4 — Deploy trên Streamlit Cloud

1. Vào [share.streamlit.io](https://share.streamlit.io)
2. Đăng nhập bằng GitHub
3. Nhấn **New app**
4. Chọn repo `tarot-app`, file `app.py`
5. Nhấn **Advanced settings** → **Secrets**
6. Thêm đoạn sau:

```toml
ANTHROPIC_API_KEY = "sk-ant-xxxxxxxxxxxxxxxx"
```

7. Nhấn **Deploy!**

---

## 💻 Chạy local (tuỳ chọn)

```bash
# Cài dependencies
pip install -r requirements.txt

# Tạo file secrets local
mkdir .streamlit
echo 'ANTHROPIC_API_KEY = "sk-ant-xxx"' > .streamlit/secrets.toml

# Chạy app
streamlit run app.py
```

---

## ✨ Tính năng

- **Nhập câu hỏi** → Tập trung tâm trí trước khi xem bài
- **Xào bài animation** → Hiệu ứng xào bài CSS đẹp mắt
- **Chọn 3 lá** → Từ bộ 78 lá, tin vào trực giác
- **Trải bài Quá Khứ – Hiện Tại – Tương Lai**
- **AI giải bài** → Claude phân tích theo câu hỏi cụ thể của bạn
- **Dark mystical theme** → Phong cách Modern Witch

---

## 🎨 Customization

Muốn thay đổi màu sắc: chỉnh file `.streamlit/config.toml`

Muốn thêm lá bài ngôn ngữ khác: chỉnh `tarot_data.py`

---

*Made with ✦ and Claude AI*
