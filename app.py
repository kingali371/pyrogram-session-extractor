from pyrogram import Client
from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import asyncio
import logging

# إعدادات التسجيل (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء تطبيق FastAPI
app = FastAPI(
    title="Pyrogram Session Extractor API",
    description="استخراج جلسات Pyrogram من حساب تليجرام",
    version="1.0.0"
)

# إضافة CORS middleware (للسماح بطلبات من أي موقع)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= نماذج البيانات (Pydantic Models) =============

class SendCodeRequest(BaseModel):
    """نموذج إرسال رمز التحقق"""
    api_id: int
    api_hash: str
    phone_number: str

class VerifyCodeRequest(BaseModel):
    """نموذج التحقق من الرمز"""
    api_id: int
    api_hash: str
    phone_number: str
    phone_code_hash: str
    code: str

class TwoFARequest(BaseModel):
    """نموذج التحقق بخطوتين (إذا كان مفعلاً)"""
    api_id: int
    api_hash: str
    phone_number: str
    phone_code_hash: str
    password: str

# ============= المسارات (Endpoints) =============

@app.get("/")
async def root():
    """الصفحة الرئيسية - التحقق من عمل API"""
    return {
        "message": "Pyrogram Session Extractor API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "send_code": "POST /send-code",
            "verify_code": "POST /verify-code",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health_check():
    """نقطة نهاية لمراقبة صحة التطبيق (لـ UptimeRobot)"""
    return {
        "status": "alive",
        "message": "Server is running",
        "timestamp": asyncio.get_event_loop().time()
    }

# دعم HEAD method لـ UptimeRobot
@app.api_route("/health", methods=["HEAD"])
async def health_check_head(response: Response):
    """نقطة نهاية HEAD لـ UptimeRobot"""
    response.headers["X-Status"] = "Alive"
    return Response(status_code=200)

@app.post("/send-code")
async def send_code(request: SendCodeRequest):
    """
    إرسال رمز التحقق إلى رقم الهاتف
    """
    try:
        logger.info(f"Sending code to: {request.phone_number}")
        
        # إنشاء عميل Pyrogram (في الذاكرة)
        app_client = Client(
            f"session_{request.api_id}_{request.phone_number}",
            api_id=request.api_id,
            api_hash=request.api_hash,
            in_memory=True
        )
        
        async with app_client:
            sent_code = await app_client.send_code(request.phone_number)
            
            logger.info(f"Code sent successfully to: {request.phone_number}")
            
            return {
                "status": "success",
                "message": "✅ تم إرسال رمز التحقق إلى تليجرام",
                "phone_code_hash": sent_code.phone_code_hash,
                "is_code_phone": getattr(sent_code, "is_code_phone", True),
                "is_code_email": getattr(sent_code, "is_code_email", False),
                "timeout": sent_code.timeout if hasattr(sent_code, "timeout") else 60
            }
            
    except Exception as e:
        logger.error(f"Error sending code: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify-code")
async def verify_code(request: VerifyCodeRequest):
    """
    التحقق من الرمز واستخراج Session String
    """
    try:
        logger.info(f"Verifying code for: {request.phone_number}")
        
        # إنشاء عميل Pyrogram
        app_client = Client(
            f"session_{request.api_id}_{request.phone_number}",
            api_id=request.api_id,
            api_hash=request.api_hash,
            in_memory=True
        )
        
        async with app_client:
            # محاولة تسجيل الدخول بالرمز
            await app_client.sign_in(
                request.phone_number,
                request.phone_code_hash,
                request.code
            )
            
            # استخراج Session String
            session_string = await app_client.export_session_string()
            
            # الحصول على معلومات الحساب
            me = await app_client.get_me()
            
            logger.info(f"Session extracted for: {me.first_name}")
            
            return {
                "status": "success",
                "message": "✅ تم استخراج الجلسة بنجاح",
                "session_string": session_string,
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "last_name": me.last_name,
                    "username": me.username,
                    "phone_number": me.phone_number,
                    "is_bot": me.is_bot
                }
            }
            
    except Exception as e:
        # التحقق من خطأ التحقق بخطوتين
        if "SESSION_PASSWORD_NEEDED" in str(e):
            raise HTTPException(
                status_code=401,
                detail="PASSWORD_NEEDED"
            )
        logger.error(f"Error verifying code: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/verify-2fa")
async def verify_2fa(request: TwoFARequest):
    """
    التحقق بخطوتين (إذا كان الحساب مفعلاً عليه 2FA)
    """
    try:
        logger.info(f"Verifying 2FA for: {request.phone_number}")
        
        app_client = Client(
            f"session_{request.api_id}_{request.phone_number}",
            api_id=request.api_id,
            api_hash=request.api_hash,
            in_memory=True
        )
        
        async with app_client:
            # تسجيل الدخول باستخدام كلمة المرور
            await app_client.sign_in(
                request.phone_number,
                request.phone_code_hash,
                password=request.password
            )
            
            # استخراج Session String
            session_string = await app_client.export_session_string()
            
            me = await app_client.get_me()
            
            return {
                "status": "success",
                "message": "✅ تم استخراج الجلسة بنجاح",
                "session_string": session_string,
                "user": {
                    "id": me.id,
                    "first_name": me.first_name,
                    "username": me.username
                }
            }
            
    except Exception as e:
        logger.error(f"Error verifying 2FA: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

# ============= تشغيل التطبيق =============
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        workers=1
    )
