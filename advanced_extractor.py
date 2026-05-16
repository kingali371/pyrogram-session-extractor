from pyrogram import Client
import asyncio
import os
import sys

class SessionExtractor:
    def __init__(self):
        self.api_id = None
        self.api_hash = None
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_banner(self):
        banner = """
╔════════════════════════════════════════╗
║     Pyrogram Session Extractor v1.0    ║
║     استخراج جلسة حساب تليجرام          ║
╚════════════════════════════════════════╝
        """
        print(banner)
        
    async def extract_session(self):
        self.clear_screen()
        self.display_banner()
        
        try:
            self.api_id = int(input("\n📱 API ID: "))
            self.api_hash = input("🔑 API HASH: ")
            
            # خيارات الجلسة
            print("\n📁 خيارات الحفظ:")
            print("1. حفظ كـ Session String فقط")
            print("2. حفظ كـ Session String وملف جلسة")
            choice = input("اختر (1/2): ")
            
            app = Client(":memory:", api_id=self.api_id, api_hash=self.api_hash)
            
            async with app:
                me = await app.get_me()
                print(f"\n✅ مرحباً {me.first_name}!")
                
                session_string = await app.export_session_string()
                
                # حفظ كملف نصي
                with open("session.txt", "w") as f:
                    f.write(session_string)
                
                if choice == "2":
                    # حفظ كملف جلسة
                    await app.stop()
                    session_app = Client("my_session", api_id=self.api_id, api_hash=self.api_hash)
                    await session_app.start()
                    print("✅ تم حفظ ملف الجلسة: my_session.session")
                    await session_app.stop()
                
                print("\n✅ تم الاستخراج بنجاح!")
                print(f"📄 حفظ في: session.txt")
                
        except ValueError:
            print("❌ خطأ: API ID يجب أن يكون رقماً")
        except Exception as e:
            print(f"❌ خطأ: {e}")

if __name__ == "__main__":
    extractor = SessionExtractor()
    asyncio.run(extractor.extract_session())
