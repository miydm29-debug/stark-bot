import os
import time
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"
MY_CHAT_ID = 6716126830
PORT = int(os.environ.get("PORT", 8080))

app_flask = Flask(__name__)
user_cookies = {}

# استقبال البيانات أوتوماتيك من سكريبت المونكي
@app_flask.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    cookie_str = data.get("cookie")
    target_link = data.get("link")
    
    if cookie_str:
        user_cookies[MY_CHAT_ID] = cookie_str
        
    if target_link and MY_CHAT_ID in user_cookies:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.midasbuy.com/"
            }
            cookies_dict = {k.strip(): v.strip() for item in user_cookies[MY_CHAT_ID].split(';') if '=' in item for k, v in [item.split('=', 1)]}
            
            # تنفيذ الطلب الفعلي
            response = requests.get(target_link, cookies=cookies_dict, headers=headers, timeout=15)
            
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": MY_CHAT_ID,
                    "text": f"🛡️ <b>STARK SYSTEM - AUTO EXECUTION</b>\n\n✅ تم تنفيذ الرابط بنجاح!\n🔗 <code>{target_link}</code>",
                    "parse_mode": "HTML"
                }
            )
            return jsonify({"status": "success"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "stored"})

@app_flask.route('/')
def home():
    return "Stark Bot Server is Running Live!"

# استقبال الروابط لو بعتها يدوي في شات البوت
async def handle_manual_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text and ("midasbuy.com" in text or "short_link" in text):
        if MY_CHAT_ID not in user_cookies:
            await update.message.reply_text("⚠️ لم يتم استقبال الكوكي من المتصفح بعد، افتح صفحة ميداسباي في ليمور أولاً!")
            return
            
        status_msg = await update.message.reply_text("🔄 جاري تنفيذ الرابط اليدوي عبر سيرفرات ميداسباي...")
        try:
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.midasbuy.com/"}
            cookies_dict = {k.strip(): v.strip() for item in user_cookies[MY_CHAT_ID].split(';') if '=' in item for k, v in [item.split('=', 1)]}
            
            response = requests.get(text.strip(), cookies=cookies_dict, headers=headers, timeout=15)
            await status_msg.edit_text(
                f"🛡️ <b>STARK SYSTEM - MANUAL EXECUTION</b>\n\n"
                f"✅ تم تنفيذ الرابط المرسل يدويًا بنجاح!\n"
                f"🔗 <code>{text.strip()}</code>",
                parse_mode="HTML"
            )
        except Exception as e:
            await status_msg.edit_text(f"❌ فشل التنفيذ: {str(e)}")
    else:
        await update.message.reply_text("⚡ أهلاً بك يا السعيد، النظام يعمل بكامل طاقته.")

def run_flask():
    app_flask.run(host="0.0.0.0", port=PORT)

def main():
    import threading
    threading.Thread(target=run_flask, daemon=True).start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_manual_message))
    app.run_polling()

if __name__ == '__main__':
    main()
