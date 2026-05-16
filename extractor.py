from pyrogram import Client
import os
import json

def create_session_file():
    """إنشاء ملف جلسة وحفظه"""
    print("🔹 استخراج جلسة Pyrogram 🔹")
    print("-" * 40)
    
    api_id = int(input("📱 API ID: "))
    api_hash = input("🔑 API HASH: ")
    
    app = Client(":memory:", api_id=api_id, api_hash=api_hash)
    
    try:
        with app:
            print("\n✅ تم تسجيل الدخول بنجاح!")
            
            # الحصول على معلومات الحساب
            me = app.get_me()
            print(f"👤 الحساب: {me.first_name} (@{me.username if me.username else 'لا يوجد'})")
            
            # استخراج الجلسة
            session_string = app.export_session_string()
            
            # حفظ في ملف
            with open("session.txt", "w") as f:
                f.write(session_string)
            
            print(f"\n✅ تم حفظ الجلسة في ملف: session.txt")
            
            # عرض أول 50 حرفاً فقط للأمان
            preview = session_string[:50] + "..."
            print(f"\n📋 Preview: {preview}")
            
            return session_string
            
    except Exception as e:
        print(f"\n❌ خطأ: {e}")
        return None

if __name__ == "__main__":
    create_session_file()
