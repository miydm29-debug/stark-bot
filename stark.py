import os
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ.get("BOT_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

app_flask = Flask('')

@app_flask.route('/')
def home():
    return "Midasbuy AI Parser Bot is running perfectly!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app_flask.run(host='0.0.0.0', port=port)

def ask_openrouter(raw_text):
    prompt = f"""
أنت مساعد ذكي ومحلل بيانات خبير. قم بتحليل النص التالي المستخرج من طلبات شبكة Midasbuy، واستخرج منه الخلاصة كاملة بدقة:
- Player ID (رقم الآي دي)
- User ID (أيدي المستخدم)
- اسم اللاعب (Name إن وجد صريحاً أو داخل التوكن)
- الـ Token أو الـ Session Token
- أي بيانات تانية مهمة

اكتب الخلاصة بشكل مرتب ونظيف جداً باللغة العربية:
{raw_text}
"""
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://t.me",
                "X-Title": "MidasbuyBot",
            },
            json={
                "model": "meta-llama/llama-3-8b-instruct:free",
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        res_json = response.json()
        if "choices" in res_json and len(res_json["choices"]) > 0:
            return res_json["choices"][0]["message"]["content"].strip()
        elif "error" in res_json:
            return f"خطأ من المزود: {res_json['error'].get('message', 'غير معروف')}"
    except Exception as e:
        return f"خطأ في الاتصال: {str(e)}"
    return "لم يتم استلام رد."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    wait_msg = await update.message.reply_text("🤖 جاري تحليل البيانات واستخراج الخلاصة...")
    
    ai_result = ask_openrouter(text)
    
    await wait_msg.edit_text(
        f"🎯 <b>الخلاصة من OpenRouter:</b>\n\n{ai_result}",
        parse_mode="HTML"
    )

def main():
    t = Thread(target=run_flask)
    t.start()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is running and listening to ALL messages...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
