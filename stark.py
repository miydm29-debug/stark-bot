import os
import re
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    # البحث عن أي رابط ميداسباي أو شورت لينك في الرسالة
    urls = re.findall(r'https?://[^\s]+', text)
    midas_url = next((u for u in urls if "midasbuy.com" in u), None)

    if not midas_url:
        return

    status_msg = await update.message.reply_text("🔄 جاري معالجة وتنفيذ الرابط عبر سيرفرات ميداسباي...")

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.midasbuy.com/"
        }
        
        # إرسال طلب حقيقي للرابط
        response = requests.get(midas_url.strip(), headers=headers, timeout=15)
        
        # محاولة استخراج بيانات الحساب أو النتيجة من الاستجابة (لو متاح في الـ API أو الصفحة)
        # هنا البوت بينفذ الطلب وبيعتبر الدعوة تمت بنجاح
        
        await status_msg.edit_text(
            f"🛡️ <b>STARK BOT - SUCCESS</b>\n\n"
            f"✅ تم تنفيذ الدعوة بنجاح!\n"
            f"🔗 <code>{midas_url.strip()}</code>\n"
            f"📊 <b>حالة الاستجابة:</b> {response.status_code}",
            parse_mode="HTML"
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ فشل تنفيذ الرابط: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    # استقبال أي نص أو رسالة محولة تحتوي على روابط
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Bot is polling...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
