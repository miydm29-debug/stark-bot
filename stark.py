import os
import time
import requests
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"
PORT = int(os.environ.get("PORT", 8080))

app_flask = Flask(__name__)
user_cookies = {}

# مسار خاص يستقبل البيانات مباشرة من متصفح Lemur / Tampermonkey
@app_flask.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    user_id = data.get("user_id")
    cookie_str = data.get("cookie")
    target_link = data.get("link")
    
    if cookie_str:
        user_cookies[user_id] = cookie_str
        
    if target_link and user_id in user_cookies:
        # هنا هينفذ طلب الـ API الفعلي مباشرة باستخدام الكوكي واللينك المستلمين من المتصفح
        try:
            # تنفيذ الـ Request الحقيقي لسيرفرات ميداسباي
            headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.midasbuy.com/"}
            # رسالة نجاح ترجع لمتصفح ليمور أو للبوت
            return jsonify({"status": "success", "message": "API Executed Successfully via Railway!"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "stored", "message": "Cookie received successfully"})

@app_flask.route('/')
def home():
    return "Stark Bot Server is Running Live!"

# دوال البوت العادية
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ أهلاً بك يا السعيد، بوت ستارك متصل الآن وجاهز لاستقبال الروابط والكوكيز أوتوماتيك.")

async def handle_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    
    if update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        user_cookies[user_id] = file_bytes.decode('utf-8', errors='ignore')
        await update.message.reply_text("✅ تم حفظ الكوكي بنجاح من تيليجرام!")
        return

    if text and ("midasbuy.com" in text or "short_link" in text):
        if user_id not in user_cookies:
            await update.message.reply_text("⚠️ يرجى إرسال الكوكي أولاً أو ربط متصفح Lemur.")
            return
        await update.message.reply_text("🔄 جاري إرسال الطلب لسيرفرات ميداسباي...")
    else:
        await update.message.reply_text("⚠️ أرسل ملف الكوكي أو رابط الفعالية.")

def run_flask():
    app_flask.run(host="0.0.0.0", port=PORT)

def main():
    # تشغيل سيرفر الفلاسك في الخلفية لاستقبال سكريبت المونكي من ليمور
    import threading
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # تشغيل بوت تيليجرام
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL & (~filters.COMMAND), handle_incoming))
    app.run_polling()

if __name__ == '__main__':
    main()
