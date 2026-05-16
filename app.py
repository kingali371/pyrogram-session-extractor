from pyrogram import Client
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio

app = FastAPI(title="Pyrogram Session Extractor")

class LoginRequest(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str

@app.get("/")
async def root():
    return {"message": "Pyrogram Session Extractor API", "status": "running"}

@app.post("/generate-session")
async def generate_session(request: LoginRequest):
    try:
        # إنشاء مجلد مؤقت للجلسة
        session_name = f"session_{request.api_id}"
        
        app_client = Client(
            session_name,
            api_id=request.api_id,
            api_hash=request.api_hash,
            in_memory=True  # تخزين الجلسة في الذاكرة
        )
        
        async with app_client:
            # إرسال طلب تسجيل الدخول
            sent_code = await app_client.send_code(request.phone_number)
            
            return {
                "status": "code_sent",
                "phone_code_hash": sent_code.phone_code_hash,
                "message": "تم إرسال رمز التحقق إلى تليجرام"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify-code")
async def verify_code(api_id: int, phone_number: str, phone_code_hash: str, code: str):
    try:
        app_client = Client(
            f"session_{api_id}",
            api_id=api_id,
            api_hash=os.getenv("API_HASH"),  # من المتغيرات البيئية
            in_memory=True
        )
        
        async with app_client:
            await app_client.sign_in(phone_number, phone_code_hash, code)
            
            # استخراج الجلسة
            session_string = await app_client.export_session_string()
            
            return {
                "status": "success",
                "session_string": session_string
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
