from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import os

# โหลด .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from database import engine, Base
from routes import navigation, admin

# สร้างตาราง database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hospital Wayfinding System",
    description="ระบบนำทางโรงพยาบาลราชวิถี",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(navigation.router)
app.include_router(admin.router)


# ==================== HTML Pages ====================
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/navigate", response_class=HTMLResponse)
async def navigate_page(request: Request):
    return templates.TemplateResponse("navigate.html", {"request": request})

@app.get("/map-editor", response_class=HTMLResponse)
async def map_editor_page(request: Request):
    return templates.TemplateResponse("map-editor.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ==================== Password Verification API ====================
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "rajavithi2024")

class PasswordRequest(BaseModel):
    password: str

@app.post("/api/verify-password")
async def verify_password(request: PasswordRequest):
    if request.password == ADMIN_PASSWORD:
        return {"success": True, "message": "รหัสผ่านถูกต้อง"}
    return {"success": False, "message": "รหัสผ่านไม่ถูกต้อง"}


# ==================== AI Chat API ====================
class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    response: str
    source: str

@app.post("/api/ai/chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    question = request.question
    
    # ตรวจสอบ API Keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    # ===== ใช้ OpenAI =====
    if openai_key and openai_key.startswith("sk-") and len(openai_key) > 20:
        try:
            import openai
            
            client = openai.OpenAI(api_key=openai_key)
            
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """คุณเป็นผู้ช่วย AI ของโรงพยาบาลราชวิถี ช่วยตอบคำถามเกี่ยวกับ:
- ตำแหน่งห้อง/แผนก/อาคาร
- เวลาทำการ
- ข้อมูลติดต่อ
- การนำทางภายในโรงพยาบาล

ข้อมูลสำคัญ:
- อาคารเฉลิมพระเกียรติฯ ชั้น 11: ห้องประชุมโยธี, ราชพฤกษ์, สุพรรณิการ์, พญาไท, ปาริชาติ
- อาคารเฉลิมพระเกียรติฯ ชั้น 12: ห้องประชุมพิบูลสงคราม
- อาคารเฉลิมพระเกียรติฯ ชั้น 9: ห้องประชุม SC, VC1, VC2, VC3, ห้องขอประวัติการรักษา
- ตึก E ชั้น 1: ห้องฉุกเฉิน (24 ชม.)
- ตึก E ชั้น 4: ห้องประชุม EMS
- ตึกสอาด ศิริพัฒน์: สถาบันโรคหัวใจ
- โทรศัพท์: 02-354-8108

ตอบเป็นภาษาไทย สั้นกระชับ ใช้ emoji เหมาะสม"""
                    },
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return ChatResponse(
                response=completion.choices[0].message.content,
                source="openai"
            )
            
        except Exception as e:
            print(f"OpenAI Error: {e}")
    
    # ===== ใช้ Anthropic Claude =====
    elif anthropic_key and anthropic_key.startswith("sk-ant-"):
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=anthropic_key)
            
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                system="คุณเป็นผู้ช่วย AI ของโรงพยาบาลราชวิถี ตอบเป็นภาษาไทย สั้นกระชับ",
                messages=[{"role": "user", "content": question}]
            )
            
            return ChatResponse(
                response=message.content[0].text,
                source="anthropic"
            )
            
        except Exception as e:
            print(f"Anthropic Error: {e}")
    
    # ===== ใช้ Local Response =====
    response = get_local_response(question)
    return ChatResponse(response=response, source="local")


def get_local_response(question: str) -> str:
    """Local AI Response - ไม่ต้องใช้ API"""
    q = question.lower()
    
    # ห้องประชุม
    if 'โยธี' in q:
        return '📍 <b>ห้องประชุมโยธี</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 11<br>ความจุประมาณ 100 คน'
    if 'ราชพฤกษ์' in q:
        return '📍 <b>ห้องประชุมราชพฤกษ์</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 11'
    if 'สุพรรณิการ์' in q:
        return '📍 <b>ห้องประชุมสุพรรณิการ์</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 11'
    if 'พญาไท' in q:
        return '📍 <b>ห้องประชุมพญาไท</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 11'
    if 'ปาริชาติ' in q:
        return '📍 <b>ห้องประชุมปาริชาติ</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 11'
    if 'พิบูล' in q:
        return '📍 <b>ห้องประชุมพิบูลสงคราม</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 12<br>ห้องประชุมใหญ่ ความจุ 200 คน'
    if 'ems' in q and 'ประชุม' in q:
        return '📍 <b>ห้องประชุม EMS</b><br>ตึก E ชั้น 4'
    if 'sc' in q or 'vc' in q:
        return '📍 <b>ห้องประชุม SC, VC1, VC2, VC3</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 9<br>หน่วยงานถ่ายทอดการพยาบาล'
    
    if 'ห้องประชุม' in q:
        return '''📋 <b>ห้องประชุม รพ.ราชวิถี</b><br><br>
<b>อาคารเฉลิมพระเกียรติฯ:</b><br>
• ชั้น 9: SC, VC1, VC2, VC3<br>
• ชั้น 11: โยธี, ราชพฤกษ์, สุพรรณิการ์, พญาไท, ปาริชาติ<br>
• ชั้น 12: พิบูลสงคราม<br><br>
<b>ตึก E:</b> ชั้น 4 - ห้องประชุม EMS'''
    
    # แผนก
    if 'ฉุกเฉิน' in q or 'er' in q:
        return '🚑 <b>ห้องฉุกเฉิน (ER)</b><br>ตึก E ชั้น 1<br>เปิด 24 ชั่วโมง'
    if 'opd' in q or 'ผู้ป่วยนอก' in q:
        return '🏥 <b>OPD ผู้ป่วยนอก</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 1-4'
    if 'หัวใจ' in q:
        return '❤️ <b>สถาบันโรคหัวใจ</b><br>ตึกสอาด ศิริพัฒน์ (ตึก G)'
    if 'ประวัติ' in q or 'เวชระเบียน' in q:
        return '📋 <b>ห้องขอประวัติการรักษา</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 9<br>ออกจากลิฟต์ตรงไปเลี้ยวขวา'
    if 'ยา' in q or 'pharmacy' in q:
        return '💊 <b>ห้องยา</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 1'
    if 'การเงิน' in q or 'จ่ายเงิน' in q:
        return '💰 <b>การเงิน</b><br>อาคารเฉลิมพระเกียรติฯ ชั้น 1'
    if 'lab' in q or 'แล็บ' in q:
        return '🔬 <b>ห้องปฏิบัติการ (Lab)</b><br>อาคารทศมินทราธิราช ชั้น 3'
    if 'x-ray' in q or 'เอกซเรย์' in q:
        return '📷 <b>X-Ray</b><br>อาคารทศมินทราธิราช ชั้น 2'
    
    # ข้อมูลทั่วไป
    if 'เวลา' in q or 'เปิด' in q or 'ปิด' in q:
        return '🕐 <b>เวลาทำการ</b><br>• OPD: 08:00-16:00 น. (จ-ศ)<br>• ฉุกเฉิน: 24 ชม.<br>• เวชระเบียน: 06:00-16:00 น.'
    if 'โทร' in q or 'เบอร์' in q or 'ติดต่อ' in q:
        return '📞 <b>ติดต่อโรงพยาบาล</b><br>โทร: 02-354-8108<br>ฉุกเฉิน: 02-354-8108 ต่อ 3000'
    if 'ที่อยู่' in q or 'อยู่ไหน' in q or 'ถนน' in q:
        return '📍 <b>ที่อยู่</b><br>2 ถนนพญาไท แขวงทุ่งพญาไท<br>เขตราชเทวี กรุงเทพฯ 10400'
    if 'สวัสดี' in q or 'หวัดดี' in q or 'hello' in q:
        return 'สวัสดีค่ะ! 😊 ยินดีให้บริการค่ะ<br>ถามได้เลยนะคะ เช่น ห้องประชุมอยู่ไหน, OPD เปิดกี่โมง'
    if 'ขอบคุณ' in q:
        return 'ยินดีค่ะ! 🙏 หากมีคำถามเพิ่มเติม ถามได้เลยนะคะ'
    
    # อาคาร
    if 'อาคาร' in q or 'ตึก' in q or 'กี่อาคาร' in q:
        return '''🏥 <b>อาคารในโรงพยาบาลราชวิถี</b><br>
• อาคารทศมินทราธิราช (25 ชั้น)<br>
• ตึกสิรินธร (18 ชั้น)<br>
• อาคารเฉลิมพระเกียรติฯ (12 ชั้น)<br>
• ตึก D-F และอื่นๆ อีก 8 อาคาร'''
    
    return '''ขอบคุณสำหรับคำถามค่ะ 🙏<br><br>
ลองถามเรื่องเหล่านี้ได้นะคะ:<br>
• ห้องประชุมต่างๆ<br>
• ตำแหน่งแผนก/ห้อง<br>
• เวลาทำการ<br>
• เบอร์ติดต่อ<br><br>
หรือโทร: <b>02-354-8108</b>'''


# ==================== API Status ====================
@app.get("/api")
async def api_info():
    return {
        "message": "Hospital Wayfinding API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/api/ai/status")
async def ai_status():
    """ตรวจสอบสถานะ AI API"""
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    
    openai_ok = bool(openai_key and openai_key.startswith("sk-") and len(openai_key) > 20)
    anthropic_ok = bool(anthropic_key and anthropic_key.startswith("sk-ant-"))
    
    return {
        "openai_configured": openai_ok,
        "anthropic_configured": anthropic_ok,
        "fallback_available": True,
        "active_provider": "openai" if openai_ok else ("anthropic" if anthropic_ok else "local"),
        "message": "ระบบ AI พร้อมใช้งาน" if (openai_ok or anthropic_ok) else "ใช้ Local AI Response"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
