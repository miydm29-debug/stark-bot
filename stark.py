import os
import re
import time
import json
import base64
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Midasbuy Bot is running successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    urls = re.findall(r'https?://[^\s]+', text)
    midas_url = next((u for u in urls if "midasbuy.com" in u), None)

    if not midas_url:
        return

    msg = await update.message.reply_text("🔍 جاري فك الرابط القصير وسحب بيانات اللاعب...")
    start_time = time.time()

    try:
        target_url = midas_url
        if "short_link" in midas_url:
            resp_redir = requests.get(midas_url, allow_redirects=True, timeout=10)
            target_url = resp_redir.url

        extracted_name = "غير معروف"
        extracted_id = "غير محدد"
        
        if "token=" in target_url:
            try:
                token_part = target_url.split("token=")[1].split("&")[0]
                padding = '=' * (-len(token_part) % 4)
                decoded_bytes = base64.urlsafe_b64decode(token_part + padding)
                decoded_data = json.loads(decoded_bytes.decode('utf-8'))
                if "name" in decoded_data:
                    extracted_name = decoded_data["name"]
                if "id" in decoded_data:
                    extracted_id = decoded_data["id"]
            except Exception:
                pass

        elapsed_time = round(time.time() - start_time, 1)

        await msg.edit_text(
            f"🎯 <b>تم استخراج بيانات الرابط بنجاح!</b>\n\n"
            f"👤 <b>الاسم:</b> {extracted_name}\n"
            f"🆔 <b>الايدي:</b> <code>{extracted_id}</code>\n"
            f"⏱️ <b>في:</b> {elapsed_time} ثانية",
            parse_mode="HTML"
        )

    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء المعالجة:\n<code>{str(e)}</code>", parse_mode="HTML")

def main():
    t = Thread(target=run_flask)
    t.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running correctly...")
    # drop_pending_updates=True بتمنع حدوث مشكلة التعارض وتقفل أي جلسة قديمة معلقة
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
