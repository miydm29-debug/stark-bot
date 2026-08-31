import os
import time
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"
MY_CHAT_ID = 6716126830  # الأيدي الخاص بك الذي استخرجناه
PORT = int(os.environ.get("PORT", 8080))

app_flask = Flask(__name__)
user_cookies = {}

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
            
            cookies_dict = {}
            for item in user_cookies[MY_CHAT_ID].split(';'):
                if '=' in item:
                    k, v = item.strip().split('=', 1)
                    cookies_dict[k] = v

            # تنفيذ الطلب الحقيقي لسيرفرات ميداسباي
            response = requests.get(target_link, cookies=cookies_dict, headers=headers, timeout=15)
            
            # إرسال النتيجة إلى بوت تيليجرام الخاص بك مباشرة
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": MY_CHAT_ID,
                    "text": f"🛡️ <b>STARK SYSTEM - AUTO EXECUTION</b>\n\n✅ تم تنفيذ الرابط بنجاح أوتوماتيك من متصفح ليمور!\n🔗 <code>{target_link}</code>",
                    "parse_mode": "HTML"
                }
            )
            
            return jsonify({"status": "success", "message": "Executed and sent to Telegram!"})
            
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "stored", "message": "Cookie received successfully"})

@app_flask.route('/')
def home():
    return "Stark Bot Server is Running Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ أهلاً يا السعيد، النظام متصل ومربوط بمتصفح ليمور بنجاح.")

def run_flask():
    app_flask.run(host="0.0.0.0", port=PORT)

def main():
    import threading
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == '__main__':
    main()
