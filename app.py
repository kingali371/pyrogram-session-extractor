from pyrogram import Client
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import os
import asyncio

app = FastAPI(title="Pyrogram Session Extractor")

# نماذج البيانات (Data Models)
class LoginRequest(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str

class VerifyRequest(BaseModel):
    api_id: int
    api_hash: str
    phone_number: str
    phone_code_hash: str
    code: str

# ============= المسارات (Endpoints) =============

@app.get("/")
async def root():
    return {"message": "Pyrogram Session Extractor API", "status": "running"}

@app.post("/send-code")
async def send_code(request: LoginRequest):
    try:
        app_client = Client(
            f"session_{request.api_id}",
            api_id=request.api_id,
            api_hash=request.api_hash,
            in_memory=True
        )
        
        async with app_client:
            sent_code = await app_client.send_code(request.phone_number)
            
            return {
                "status": "code_sent",
                "phone_code_hash": sent_code.phone_code_hash,
                "message": "✅ تم إرسال رمز التحقق إلى تليجرام"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify-code")
async def verify_code(request: VerifyRequest):
    try:
        app_client = Client(
            f"session_{request.api_id}",
            api_id=request.api_id,
            api_hash=request.api_hash,
            in_memory=True
        )
        
        async with app_client:
            await app_client.sign_in(
                request.phone_number, 
                request.phone_code_hash, 
                request.code
            )
            
            session_string = await app_client.export_session_string()
            
            return {
                "status": "success",
                "session_string": session_string,
                "message": "✅ تم استخراج الجلسة بنجاح"
            }
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= مسار Health Check لـ UptimeRobot =============

@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check(response: Response):
    """نقطة نهاية خفيفة لـ UptimeRobot"""
    response.headers["X-Status"] = "Alive"
    return {"status": "ok", "message": "Server is running"}

# ============= تشغيل التطبيق =============

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
