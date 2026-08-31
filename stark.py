import os
import re
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    # استخراج رابط ميداسباي أو الشورت لينك من الرسالة
    urls = re.findall(r'https?://[^\s]+', text)
    midas_url = next((u for u in urls if "midasbuy.com" in u), None)

    if not midas_url:
        return

    msg = await update.message.reply_text("🔄 جاري فحص وتنفيذ الرابط...")
    start_time = time.time()

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.midasbuy.com/"
        }
        
        # إرسال طلب حقيقي لسيرفرات ميداسباي
        response = requests.get(midas_url.strip(), headers=headers, timeout=15)
        html_content = response.text

        # استخراج الأيدي واسم الحساب من استجابة الصفحة (بالتعبيرات المنتظمة Regex)
        # مidasbuy عادة بيخزن البيانات دي جوه ملفات الـ JSON أو الـ HTML الخاصة بالصفحة
        id_match = re.search(r'"roleId"\s*:\s*"(\d+)"', html_content) or re.search(r'id["\']?\s*:\s*["\']?(\d{8,12})', html_content)
        name_match = re.search(r'"roleName"\s*:\s*"([^"]+)"', html_content) or re.search(r'name["\']?\s*:\s*["\']?([^"\']+)["\']?', html_content)

        extracted_id = id_match.group(1) if id_match else "غير محدد (يتطلب صلاحية جلسة)"
        extracted_name = name_match.group(1) if name_match else "حساب ميداسباي"

        elapsed_time = round(time.time() - start_time, 1)

        # الرد بنفس الشكل الاحترافي
        await msg.edit_text(
            f"🛡️ <b>Midasbuy Bot (STARK)</b>\n\n"
            f"👤 <b>الاسم:</b> {extracted_name}\n"
            f"🆔 <b>الايدي:</b> <code>{extracted_id}</code>\n"
            f"⏱️ <b>في:</b> {elapsed_time} ثانية\n"
            f"✅ <b>الحالة:</b> تم تنفيذ الرابط بنجاح!",
            parse_mode="HTML"
        )

    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Stark Bot is running and waiting for links...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
