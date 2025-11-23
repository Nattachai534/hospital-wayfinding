# 🏥 ระบบนำทางโรงพยาบาลราชวิถี

ระบบนำทางอัจฉริยะสำหรับโรงพยาบาลราชวิถี พร้อม AI ผู้ช่วยตอบคำถาม

## ✨ Features

- 🗺️ แผนที่นำทางภายในโรงพยาบาล
- 🤖 AI ผู้ช่วยตอบคำถาม (รองรับ OpenAI & Anthropic)
- 🔊 เสียงนำทางภาษาไทย (Text-to-Speech)
- 📱 รองรับ Mobile & Desktop
- 📋 ข้อมูลห้องประชุมครบถ้วน

## 🏢 อาคารที่รองรับ

1. อาคารทศมินทราธิราช (25 ชั้น)
2. ตึกสิรินธร (18 ชั้น)
3. อาคารเฉลิมพระเกียรติฯ (12 ชั้น)
4. ตึกอำนวยการ (5 ชั้น)
5. ตึกอุบัติเหตุและฉุกเฉิน (4 ชั้น)
6. ตึกอายุรกรรม (6 ชั้น)
7. ตึกสอาด ศิริพัฒน์ (8 ชั้น)
8. และอื่นๆ อีก 4 อาคาร

## 🚀 Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template)

### ขั้นตอน:

1. Fork repository นี้
2. ไปที่ [Railway.app](https://railway.app)
3. เลือก "Deploy from GitHub repo"
4. เลือก repository ที่ fork ไว้
5. เพิ่ม Environment Variable (optional):
   - `OPENAI_API_KEY` - สำหรับ AI Chat

## 💻 Run Locally

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/hospital-wayfinding.git
cd hospital-wayfinding

# Install
pip install -r requirements.txt

# Run
python main.py
```

เปิด http://localhost:8000

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PORT` | Server port | Auto (Railway) |
| `OPENAI_API_KEY` | OpenAI API Key | Optional |
| `ANTHROPIC_API_KEY` | Anthropic API Key | Optional |

## 📁 Project Structure

```
hospital-wayfinding/
├── main.py              # FastAPI app
├── database.py          # Database config
├── requirements.txt     # Dependencies
├── Procfile            # Railway/Heroku
├── templates/          # HTML templates
│   ├── index.html      # หน้าหลัก
│   ├── navigate.html   # หน้านำทาง
│   ├── admin.html      # Admin panel
│   └── map-editor.html # Map editor
├── static/
│   └── images/maps/    # แผนที่
└── routes/
    ├── navigation.py   # Navigation API
    └── admin.py        # Admin API
```

## 📞 Contact

โรงพยาบาลราชวิถี
- โทร: 02-354-8108
- เว็บไซต์: https://www.rajavithi.go.th

---
Made with ❤️ for Rajavithi Hospital
