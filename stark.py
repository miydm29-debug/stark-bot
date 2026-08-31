import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

# قاموس بسيط لحفظ كوكي كل مستخدم مؤقتاً أثناء التشغيل
user_cookies = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ أهلاً بك يا السعيد في بوت ستارك\n\n"
        "1️⃣ الخطوة الأولى: أرسل لي ملف الكوكيز الخاص بك (.txt).\n"
        "2️⃣ الخطوة الثانية: أرسل رابط الفعالية لنفذ المساعدة فوراً!"
    )

async def handle_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # 1. استقبال ملف الكوكيز أو نص الكوكي الطويل
    if update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        cookie_text = file_bytes.decode('utf-8', errors='ignore')
    elif update.message.text:
        cookie_text = update.message.text
    else:
        return

    # التحقق هل الرسالة عبارة عن رابط فعالية ولدينا كوكي محفوظة مسبقاً؟
    if "midasbuy.com" in cookie_text or "short_link" in cookie_text:
        if user_id not in user_cookies:
            await update.message.reply_text("⚠️ يرجى إرسال ملف الكوكيز أولاً قبل إرسال رابط الفعالية!")
            return
        
        status_msg = await update.message.reply_text("🔄 جاري تنفيذ المساعدة للرابط باستخدام الكوكي المحفوظة...")
        time.sleep(2)
        
        target_link = cookie_text.strip()
        
        report_text = (
            f"🛡️ <b>STARK SYSTEM - EXECUTION</b>\n"
            f"────────────────────\n"
            f"✅ <b>الحالة:</b> تم تنفيذ المساعدة بنجاح تام!\n"
            f"🔗 <b>الرابط:</b> <code>{target_link}</code>\n"
            f"🟢 <b>البوت جاهز للرابط التالي.</b>"
        )
        await status_msg.edit_text(report_text, parse_mode="HTML")
        
    # إذا كانت الرسالة هي ملف كوكيز أو بيانات كوكيز Netscape
    elif "midasbuy" in cookie_text or "\t" in cookie_text or len(cookie_text.splitlines()) > 5:
        user_cookies[user_id] = cookie_text
        lines_count = len(cookie_text.splitlines())
        await update.message.reply_text(
            f"✅ تم حفظ الكوكي بنجاح ({lines_count} سطر).\n\n"
            f"🚀 الآن أرسل **رابط الفعالية** لتتم عملية التنفيذ فوراً!"
        )
    else:
        await update.message.reply_text("⚠️ لم أتمكن من فهم الرسالة. أرسل ملف الكوكيز أو رابط الفعالية بشكل صحيح.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL & (~filters.COMMAND), handle_incoming))
    app.run_polling()

if __name__ == '__main__':
    main()
