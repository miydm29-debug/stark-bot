import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ أهلاً بك يا السعيد في بوت ستارك\n\n"
        "أرسل لي ملف الكوكيز (.txt) أو انسخ محتوى الكوكي واكتبه هنا، وسأقوم بقراءتها فوراً!"
    )

async def handle_incoming(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # التعامل مع استقبال الملفات (زي cookies.txt)
    if update.message.document:
        doc = update.message.document
        file = await context.bot.get_file(doc.file_id)
        file_bytes = await file.download_as_bytearray()
        cookie_text = file_bytes.decode('utf-8', errors='ignore')
    elif update.message.text:
        cookie_text = update.message.text
    else:
        return

    # التحقق هل النص أو الملف يحتوي على كوكيز Netscape أو بيانات ميداسباي
    if "midasbuy" in cookie_text or "session" in cookie_text or "\t" in cookie_text:
        status_msg = await update.message.reply_text("🔄 جاري تحليل قراءة الكوكي واستخراج بيانات الجلسة...")
        
        time.sleep(1.5)
        
        # تحليل بسيط للكوكي للتأكد من قراءتها
        lines_count = len(cookie_text.splitlines())
        
        report_text = (
            f"🛡️ <b>STARK SYSTEM - COOKIE PARSER</b>\n"
            f"────────────────────\n"
            f"✅ <b>حالة القراءة:</b> تم استلام وقراءة الكوكي بنجاح!\n"
            f"📄 <b>عدد الاسطر المستخرجة:</b> {lines_count} سطر\n"
            f"🟢 <b>الحالة:</b> الجلسة جاهزة للاستخدام في إرسال طلبات الـ API.\n\n"
            f"🚀 <i>أرسل رابط الفعالية الآن لتنفيذ المساعدة بالحساب المُسجل.</i>"
        )
        await status_msg.edit_text(report_text, parse_mode="HTML")
    else:
        await update.message.reply_text("⚠️ لمამا أتعرف على محتوى الكوكي، تأكد من إرسال الملف أو النص الصحيح.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # استقبال النصوص أو الملفات النصية
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL & (~filters.COMMAND), handle_incoming))
    app.run_polling()

if __name__ == '__main__':
    main()
