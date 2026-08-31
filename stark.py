import json
import logging
import re
from flask import Flask, jsonify, request
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8967404868:AAFcNtlTD3IlqjjCeHgTIHVj0agPEUostSg"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
MIDASBUY_API_URL = "https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_prize_service/QueryPrizeInfoList"


def send_telegram_message(chat_id, text):
  """إرسال رد للمستخدم عبر تليجرام"""
  url = f"{TELEGRAM_API_URL}/sendMessage"
  data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
  try:
    requests.post(url, json=data, timeout=5)
  except Exception as e:
    logger.error(f"Error sending message: {e}")


@app.route("/", methods=["GET"])
def index():
  return "Bot Server is Running active!", 200


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
  update = request.get_json(silent=True)
  if not update or "message" not in update:
    return jsonify({"status": "ignored"}), 200

  message = update["message"]
  chat_id = message["chat"]["id"]
  text = message.get("text", "")

  # طباعة الرسالة الواردة في السيرفر للمتابعة
  logger.info(f"Received message: {text[:50]}...")

  if text.strip() == "/start":
    send_telegram_message(
        chat_id,
        "👋 أهلاً بك! أرسل كود الـ cURL أو الـ JSON وسأقوم بمعالجته فوراً.",
    )
    return jsonify({"status": "ok"}), 200

  # البحث المباشر عن player_id في النص بغض النظر عن طوله
  p_match = re.search(r'["\']?player_id["\']?\s*[:=]\s*["\']?(\d+)["\']?', text)

  if p_match:
    player_id = p_match.group(1)

    # استخراج الـ user_id أو استخدام قيمة افتراضية
    u_match = re.search(
        r'["\']?(?:user_id|openid)["\']?\s*[:=]\s*["\']?(\d+|U[a-zA-Z0-9]+)["\']?',
        text,
    )
    user_id = (
        u_match.group(1) if u_match else "184958050392999208"
    )

    send_telegram_message(
        chat_id,
        f"⏳ تم العثور على Player ID: <code>{player_id}</code>\nجاري إرسال الطلب"
        " لـ Midasbuy...",
    )

    # إعداد الطلب لـ Midasbuy
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "origin": "https://www.midasbuy.com",
        "referer": "https://www.midasbuy.com/",
        "user-agent": "Mozilla/5.0",
        "x-tencent-login-check": json.dumps({
            "accountType": "midasbuy",
            "appid": "123123",
            "endpoint_type": "mpgo_activity",
            "offer_id": "1450015065",
            "openid": user_id,
            "openkey": "nokey",
            "pf": "mds_pc_browser-v2-android-midasweb",
            "session_id": "hy_gameid",
            "session_type": "st_dummy",
            "token": (
                "146163c10927d20b2c0c970bc46d8b619b2dee969aad2913b87de992a6e242eb"
            ),
            "userType": "hy_gameid",
        }),
    }

    payload = {
        "mp_activity_id": "Activity_1784618952_EQXYLI",
        "mp_app_id": "1450015065",
        "user_id": user_id,
        "user_id_type": "hy_gameid",
        "query_page_num": 1,
        "query_page_size": 20,
        "mp_success_record": 1,
        "mp_sub_activity_id_list": ["1784618952184505661TLS"],
        "mp_prize_is_open_model": True,
        "meta_data": {
            "ori_zoneid": "1",
            "client_ver": "android",
            "server_id": "1",
            "role_id": "",
            "muid": "U24tqg0cyjq0wp",
            "player_id": player_id,
            "pf": "false.",
        },
    }

    try:
      resp = requests.post(
          MIDASBUY_API_URL, headers=headers, json=payload, timeout=10
      )
      reply_text = (
          f"✅ <b>تم إرسال الطلب بنجاح!</b>\n• <b>Code:</b>"
          f" {resp.status_code}\n• <b>الرد:</b>\n<pre>{resp.text[:500]}</pre>"
      )
    except Exception as e:
      reply_text = f"❌ حدث خطأ أثناء الاتصال بـ Midasbuy: {str(e)}"

    send_telegram_message(chat_id, reply_text)
  else:
    # لو النص مفيش فيه player_id عشان نتاكد إن البوت استقبل الرسالة أصلاً
    send_telegram_message(
        chat_id,
        "⚠️ تم استقبال رسالتك، ولكن لم يتم العثور على <code>player_id</code>"
        " بداخلها.",
    )

  return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
