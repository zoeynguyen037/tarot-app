# 🔮 Tarot Reading App

Ứng dụng xem tarot 3 lá (Quá khứ · Hiện tại · Tương lai) theo phong cách tâm lý học, sử dụng Claude API.

---

## Deploy lên Streamlit Cloud

### Bước 1 — Push lên GitHub
```bash
git init
git add .
git commit -m "first commit"
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```

### Bước 2 — Deploy trên Streamlit Cloud
1. Vào [share.streamlit.io](https://share.streamlit.io) → **New app**
2. Chọn repo GitHub vừa push
3. Main file: `app.py`
4. Vào **Advanced settings → Secrets**, thêm:
```toml
ANTHROPIC_API_KEY = "sk-ant-xxxx"
```
5. Bấm **Deploy** — xong!

---

## Chạy local

```bash
pip install -r requirements.txt

# Tạo file .streamlit/secrets.toml và điền API key
streamlit run app.py
```

---

## Cấu trúc
```
tarot-app/
├── app.py              # Main Streamlit app
├── cards.py            # Database 78 lá tarot
├── requirements.txt
├── .gitignore
└── .streamlit/
    └── secrets.toml    # API key (không commit lên GitHub)
```
