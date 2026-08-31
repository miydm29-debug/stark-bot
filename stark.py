import os
import threading
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"
MY_CHAT_ID = 6716126830
PORT = int(os.environ.get("PORT", 8080))

app_flask = Flask(__name__)
user_cookies = {}

# 1. استقبال الكوكي ورابط المتصفح أوتوماتيك من Tampermonkey
@app_flask.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    
    cookie_str = data.get("cookie")
    if cookie_str and len(cookie_str) > 20:
        user_cookies[MY_CHAT_ID] = cookie_str
        return jsonify({"status": "success", "message": "Cookie saved!"})
    
    return jsonify({"status": "error", "message": "Invalid cookie"})

@app_flask.route('/')
def home():
    return "Stark Bot Active!"

# دالة تنفيذ الرابط وإرسال النتيجة لتيليجرام
def execute_and_reply(link_text, chat_id):
    if chat_id not in user_cookies:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": "⚠️ لم يتم حفظ الكوكي بعد! افتح صفحة ميداسباي في متصفح ليمور أولاً ليتم سحبها."
        })
        return

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.midasbuy.com/"
        }
        cookies_dict = {k.strip(): v.strip() for item in user_cookies[chat_id].split(';') if '=' in item for k, v in [item.split('=', 1)]}
        
        # تنفيذ الطلب الفعلـي للرابط المرسل
        response = requests.get(link_text.strip(), cookies=cookies_dict, headers=headers, timeout=15)
        
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"🛡️ <b>STARK SYSTEM - MANUAL LINK EXECUTION</b>\n\n"
                        f"✅ تم تنفيذ الرابط الذي أرسلته بنجاح!\n"
                        f"🔗 <code>{link_text.strip()}</code>\n"
                        f"📊 <b>حالة السيرفر:</b> {response.status_code}",
                "parse_mode": "HTML"
            }
        )
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"❌ فشل تنفيذ الرابط: {str(e)}"
        })

# 2. استقبال الرابط لو بعته في شات البوت يدوي
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.effective_chat.id
    
    # التأكد إن الرسالة فيها رابط ميداسباي أو شورت لينك
    if text and ("midasbuy.com" in text or "short_link" in text):
        # استخراج الرابط بالتحديد من النص لو معاه كلام تاني
        import re
        urls = re.findall(r'https?://[^\s]+', text)
        target_url = next((u for u in urls if "midasbuy.com" in u), text)
        
        await update.message.reply_text("🔄 جاري تنفيذ الرابط أوتوماتيك عبر سيرفرات ميداسباي باستخدام الكوكي المحفوظة...")
        
        # تشغيل التنفيذ في خلفية مستقلة عشان البوت ميهنجش
        threading.Thread(target=execute_and_reply, args=(target_url, chat_id)).start()

def run_telegram_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    # تشغيل بوت تيليجرام في خيط منفصل لتفادي تعارض الـ Conflict وتوافقاً مع فلاسك
    t = threading.Thread(target=run_telegram_bot)
    t.daemon = True
    t.start()

    # تشغيل سيرفر فلاسك الأساسي على ريلواي
    app_flask.run(host="0.0.0.0", port=PORT)
