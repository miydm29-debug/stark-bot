import os
import threading
import re
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"
MY_CHAT_ID = 6716126830
PORT = int(os.environ.get("PORT", 8080))

app_flask = Flask(__name__)
user_cookies = {}

@app_flask.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    
    cookie_str = data.get("cookie")
    if cookie_str and len(cookie_str) > 20:
        user_cookies[MY_CHAT_ID] = cookie_str
        return jsonify({"status": "success"})
    return jsonify({"status": "error"})

@app_flask.route('/')
def home():
    return "Stark Bot Active!"

def execute_and_reply(link_text, chat_id):
    if chat_id not in user_cookies:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": "⚠️ لم يتم حفظ الكوكي! افتح ميداسباي في ليمور لثانية واحدة."
        })
        return

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.midasbuy.com/"
        }
        cookies_dict = {k.strip(): v.strip() for item in user_cookies[chat_id].split(';') if '=' in item for k, v in [item.split('=', 1)]}
        
        response = requests.get(link_text.strip(), cookies=cookies_dict, headers=headers, timeout=15)
        
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": f"🛡️ <b>STARK SYSTEM - SUCCESS</b>\n\n✅ تم تنفيذ الدعوة بنجاح!\n🔗 <code>{link_text.strip()}</code>",
                "parse_mode": "HTML"
            }
        )
    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
            "chat_id": chat_id,
            "text": f"❌ خطأ أثناء التنفيذ: {str(e)}"
        })

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    chat_id = update.effective_chat.id
    
    if text:
        # البحث عن أي رابط ميداسباي في النص مهما كان طويل أو محول
        urls = re.findall(r'https?://[^\s]+', text)
        midas_url = next((u for u in urls if "midasbuy.com" in u), None)
        
        if midas_url:
            await update.message.reply_text("🔄 جاري تنفيذ الدعوة بالكوكي المحفوظة...")
            threading.Thread(target=execute_and_reply, args=(midas_url, chat_id)).start()

def run_telegram_bot():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & (~filters.COMMAND), handle_message))
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    threading.Thread(target=run_telegram_bot, daemon=True).start()
    app_flask.run(host="0.0.0.0", port=PORT)
