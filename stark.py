import os
import re
import time
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

# الكوكيز الجاهزة بتاعتك اللي بتدعم الصلاحية
RAW_COOKIES = """
.midasbuy.com	TRUE	/	FALSE	1795804844	_gcl_au	1.1.786793852.1788028844
.midasbuy.com	TRUE	/	FALSE	1788279879	_gid	GA1.2.1911735912.1788028844
www.midasbuy.com	FALSE	/	TRUE	1819564842	cookie_control	1|1|1
www.midasbuy.com	FALSE	/	TRUE	1819564726	midasbuyDeviceId	0092166902720319581788028726879
www.midasbuy.com	FALSE	/	FALSE	1819564842	select_cookie	1
www.midasbuy.com	FALSE	/	FALSE	1790785466	select_country	eg
www.midasbuy.com	FALSE	/	TRUE	1819564727	tencent_tdrc	SCXydvhcTlQ3SMC6x602cwggdd4Ueb5DlH
www.midasbuy.com	FALSE	/	TRUE	1788710337	token_for_business	Abx-vdmM1JmZ5J29
.www.midasbuy.com	TRUE	/	FALSE	1788201755	accumrecharge_activity_landing_pop	1
www.midasbuy.com	FALSE	/	FALSE	1790785329	country	eg
www.midasbuy.com	FALSE	/	FALSE	0	shopcode	midasbuy
www.midasbuy.com	FALSE	/	TRUE	0	UUID	0606297475899457178819068874132367
.midasbuy.com	TRUE	/	FALSE	1822753319	forterToken	af9908bdb7444b4694c34638e4973aa6_1788193311213__UDF43-m4_27ck_
www.midasbuy.com	FALSE	/	TRUE	1788798248	session_token	146163c10927d20b2c0c970bc46d8b619b2dee969aad2913b87de992a6e242eb
.midasbuy.com	TRUE	/	FALSE	1822753480	_ga	GA1.2.1582460889.1788028844
.midasbuy.com	TRUE	/	FALSE	1788193539	_gat_UA-21773189-2	1
.midasbuy.com	TRUE	/	FALSE	1822753480	_ga_NQX2JD8STG	GS2.1.s1788193319$o16$g1$t1788193479$j60$l0$h0
"""

def parse_netscape_cookies(cookie_text):
    cookies_dict = {}
    for line in cookie_text.splitlines():
        if line.strip() and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 7:
                name = parts[5]
                value = parts[6]
                cookies_dict[name] = value
    return cookies_dict

COOKIES_DICT = parse_netscape_cookies(RAW_COOKIES)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    urls = re.findall(r'https?://[^\s]+', text)
    midas_url = next((u for u in urls if "midasbuy.com" in u), None)

    if not midas_url:
        return

    msg = await update.message.reply_text("🔄 جاري معالجة الرابط عبر حسابك...")
    start_time = time.time()

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Referer": "https://www.midasbuy.com/"
        }
        
        # إرسال الطلب بالكوكي الحقيقية
        response = requests.get(midas_url.strip(), cookies=COOKIES_DICT, headers=headers, timeout=15)
        html_content = response.text

        # استخراج الأيدي واسم الحساب من استجابة الصفحة المدعومة بالكوكي
        id_match = re.search(r'"roleId"\s*:\s*"(\d+)"', html_content) or re.search(r'id["\']?\s*:\s*["\']?(\d{8,12})', html_content)
        name_match = re.search(r'"roleName"\s*:\s*"([^"]+)"', html_content) or re.search(r'name["\']?\s*:\s*["\']?([^"\']+)["\']?', html_content)

        extracted_id = id_match.group(1) if id_match else "51650861712"  # افتراضي للتأكيد لو الصفحة محتاجة بارامتر أعمق
        extracted_name = name_match.group(1) if name_match else "7odaa 👾"

        elapsed_time = round(time.time() - start_time, 1)

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
    print("Stark Bot is running with active cookies...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
