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

# قراءة التوكن والمفتاح من متغيرات البيئة بأمان تام
BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Midasbuy Bot is running successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

# دالة لطلب الذكاء الاصطناعي Gemma من OpenRouter
def ask_gemma(prompt_text):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://t.me",
                "X-Title": "MidasbuyBot",
            },
            data=json.dumps({
                "model": "google/gemma-4-31b-it:free",
                "messages": [
                    {"role": "user", "content": prompt_text}
                ]
            }),
            timeout=15
        )
        res_json = response.json()
        if "choices" in res_json:
            return res_json["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطأ في الاتصال بـ Gemma: {str(e)}"
    return "لم يتم استلام رد من النموذج."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    # لو المستخدم بدأ الرسالة بكلمة "ai" نوجهه لـ Gemma مباشرة
    if text.lower().startswith("ai "):
        query = text[3:].strip()
        wait_msg = await update.message.reply_text("🤖 جاري التفكير...")
        ai_reply = ask_gemma(query)
        await wait_msg.edit_text(f"💡 <b>رد الذكاء الاصطناعي:</b>\n\n{ai_reply}", parse_mode="HTML")
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

        if extracted_id == "غير محدد":
            ai_analysis = ask_gemma(f"استخرج فقط رقم الايدي (ID) واسم اللاعب من هذا الرابط أو النص بدون أي كلام إضافي: {target_url}")
            extracted_name = f"تحليل ذكي: {ai_analysis[:50]}"

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
    print("Bot is running correctly with Gemma integration...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
