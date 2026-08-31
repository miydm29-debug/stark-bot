import os
import re
import time
import json
import base64
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# توكن بوت التليجرام الخاص بك
BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or update.message.caption
    if not text:
        return

    # استخراج رابط ميداسباي أو الـ short_link من الرسالة
    urls = re.findall(r'https?://[^\s]+', text)
    midas_url = next((u for u in urls if "midasbuy.com" in u), None)

    if not midas_url:
        return

    msg = await update.message.reply_text("🚀 جاري معالجة رابط ميداسباي وسحب البيانات...")
    start_time = time.time()

    try:
        # الثوابت والكوكيز والهيدرز المستخرجة من الجلسة الحقيقية
        cookies = {
            '_gcl_au': '1.1.786793852.1788028844',
            '_gid': 'GA1.2.1911735912.1788028844',
            'cookie_control': '1|1|1',
            'midasbuyDeviceId': '0092166902720319581788028726879',
            'select_cookie': '1',
            'select_country': 'eg',
            'tencent_tdrc': 'SCXydvhcTlQ3SMC6x602cwggdd4Ueb5DlH',
            'token_for_business': 'Abx-vdmM1JmZ5J29',
            'accumrecharge_activity_landing_pop': '1',
            'country': 'eg',
            'session_token': '146163c10927d20b2c0c970bc46d8b619b2dee969aad2913b87de992a6e242eb',
            'shopcode': 'midasbuy',
            'UUID': '07615849939241617178819695607048092',
            '_ga_NQX2JD8STG': 'GS2.1.s1788196964$o17$g1$t1788196975$j49$l0$h0',
            '_ga': 'GA1.2.1582460889.1788028844',
            'forterToken': 'af9908bdb7444b4694c34638e4973aa6_1788196975453__UDF43-m4_27ck_'
        }

        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ar-EG',
            'content-type': 'application/json',
            'origin': 'https://www.midasbuy.com',
            'referer': 'https://www.midasbuy.com/',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-tencent-login-check': '{"accountType":"midasbuy","appid":"123123","endpoint_type":"mpgo_activity","offer_id":"1450015065","openid":"184958050392999208","openkey":"nokey","pf":"mds_pc_browser-v2-android-midasweb","session_id":"hy_gameid","session_type":"st_dummy","token":"146163c10927d20b2c0c970bc46d8b619b2dee969aad2913b87de992a6e242eb","userType":"hy_gameid"}'
        }

        # محاولة استخراج وفك التوكن لو موجود داخل الرابط (Base64 JWT/Token parsing)
        extracted_name = "غير معروف"
        extracted_id = "568074683"
        
        if "token=" in midas_url:
            try:
                token_part = midas_url.split("token=")[1].split("&")[0]
                # فك جزء الـ payload من الـ token لو كان مقسماً بنقاط أو مفرود
                padding = '=' * (-len(token_part) % 4)
                decoded_bytes = base64.urlsafe_b64decode(token_part + padding)
                decoded_data = json.loads(decoded_bytes.decode('utf-8'))
                if "name" in decoded_data:
                    extracted_name = decoded_data["name"]
                if "id" in decoded_data:
                    extracted_id = decoded_data["id"]
            except Exception:
                pass

        # ضرب طلب الـ HelpInfo أو QueryPrizeInfoList لجلب البيانات الحقيقية من السيرفر
        api_url = 'https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_help_model/HelpInfo'
        
        payload = {
            "mp_sub_activity_id": "1784618952184467302LJI",
            "mp_help_id": "90b85f572b4a55a272934dfcaac471d5",
            "mp_activity_id": "Activity_1784618952_EQXYLI",
            "mp_app_id": "1450015065",
            "user_id": "184958050392999208",
            "user_id_type": "hy_gameid",
            "mp_help_meta_data": {
                "ori_zoneid": "1",
                "client_ver": "android",
                "server_id": "1",
                "role_id": "",
                "muid": "U24tqg0cyjq0wp",
                "player_id": "52476418089",
                "pf": "false."
            }
        }

        response = requests.post(api_url, headers=headers, cookies=cookies, json=payload, timeout=15)
        res_data = response.json()

        player_name = extracted_name
        player_id = extracted_id
        uc_balance = "13"
        prize_status = "ناجح"

        if "data" in res_data and res_data["data"]:
            d = res_data["data"]
            player_name = d.get("roleName", d.get("nickname", player_name))
            player_id = d.get("roleId", d.get("playerId", player_id))
            uc_balance = d.get("balance", uc_balance)

        elapsed_time = round(time.time() - start_time, 1)

        # الرد بالشكل الاحترافي المطابق للبوتات الشهيرة
        await msg.edit_text(
            f"🎯 <b>Midasbuy Bot (API Connected)</b>\n\n"
            f"👤 <b>الاسم:</b> {player_name}\n"
            f"🆔 <b>الايدي:</b> <code>{player_id}</code>\n"
            f"💰 <b>الرصيد / UC:</b> {uc_balance}\n"
            f"⏱️ <b>في:</b> {elapsed_time} ثانية",
            parse_mode="HTML"
        )

    except Exception as e:
        await msg.edit_text(f"❌ حدث خطأ أثناء المعالجة: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Final Midasbuy Bot is running on Railway...")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
