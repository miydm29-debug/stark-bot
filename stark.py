import json
import logging
import re
from flask import Flask, jsonify, request
import requests

# إعداد التسجيل (Logging)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ==================== الإعدادات الأساسية ====================
TELEGRAM_BOT_TOKEN = "8967404868:AAFcNtlTD3IlqjjCeHgTIHVj0agPEUostSg"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

MIDASBUY_API_URL = "https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_prize_service/QueryPrizeInfoList"


# ==================== الدوال المساعدة ====================
def extract_credentials(text):
  """دالة مرنة لاستخراج (Player ID, User ID, Token) من أي كود cURL أو Fetch أو JSON"""
  player_id, user_id, token = None, None, None

  # 1. استخراج Player ID
  p_match = re.search(r'["\']?player_id["\']?\s*[:=]\s*["\']?(\d+)["\']?', text)
  if p_match:
    player_id = p_match.group(1)

  # 2. استخراج User ID / OpenID
  u_match = re.search(
      r'["\']?(?:user_id|openid)["\']?\s*[:=]\s*["\']?(\d+|U[a-zA-Z0-9]+)["\']?',
      text,
  )
  if u_match:
    user_id = u_match.group(1)

  # 3. استخراج Token
  t_match = re.search(
      r'["\']?token["\']?\s*[:=]\s*["\']?([a-fA-F0-9]{32,64}|ey[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*)["\']?',
      text,
  )
  if t_match:
    token = t_match.group(1)

  return player_id, user_id, token


def execute_midasbuy_request(player_id, user_id, token):
  """إرسال الطلب لـ Midasbuy بنفس التوكن والمعرفات"""
  # افتراض قيم احتياطية إذا كانت بعض القيم ناقصة
  user_id = user_id or "184958050392999208"
  token = (
      token
      or "146163c10927d20b2c0c970bc46d8b619b2dee969aad2913b87de992a6e242eb"
  )

  headers = {
      "accept": "application/json, text/plain, */*",
      "accept-language": "ar-EG",
      "content-type": "application/json",
      "origin": "https://www.midasbuy.com",
      "referer": "https://www.midasbuy.com/",
      "user-agent": (
          "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like"
          " Gecko) Chrome/127.0.0.0 Safari/537.36"
      ),
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
          "token": token,
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
    response = requests.post(
        MIDASBUY_API_URL, headers=headers, json=payload, timeout=12
    )
    return response.status_code, response.json()
  except requests.exceptions.JSONDecodeError:
    return response.status_code, response.text
  except Exception as e:
    return 500, str(e)


def send_telegram_message(chat_id, text):
  """إرسال رد للمستخدم عبر تليجرام"""
  url = f"{TELEGRAM_API_URL}/sendMessage"
  data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
  try:
    requests.post(url, json=data, timeout=5)
  except Exception as e:
    logger.error(f"Error sending message: {e}")


# ==================== الـ Webhook الخاص بالسيرفر ====================
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

  # رسالة الترحيب /start
  if text.strip() == "/start":
    send_telegram_message(
        chat_id,
        "👋 <b>أهلاً بك!</b>\nأرسل كود cURL أو Fetch أو بيانات الميداسباي"
        " وسيتم استخراج المعرفات وتطبيق الطلب فوراً.",
    )
    return jsonify({"status": "ok"}), 200

  # تحليل النص واستخراج البيانات
  player_id, user_id, token = extract_credentials(text)

  if player_id:
    send_telegram_message(
        chat_id,
        f"⏳ <b>تم العثور على المعرفات:</b>\n• Player ID:"
        f" <code>{player_id}</code>\n• User ID:"
        f" <code>{user_id or 'افتراضي'}</code>\n\nجاري إرسال الطلب لـ"
        " Midasbuy...",
    )

    status_code, response_data = execute_midasbuy_request(
        player_id, user_id, token
    )

    reply_text = (
        f"✅ <b>اكتمل الطلب!</b>\n"
        f"• <b>Status Code:</b> {status_code}\n"
        f"• <b>الاستجابة:</b>\n<pre>{json.dumps(response_data, ensure_ascii=False, indent=2) if isinstance(response_data, dict) else response_data}</pre>"
    )
    send_telegram_message(chat_id, reply_text)
  else:
    send_telegram_message(
        chat_id,
        "❌ لم يتم العثور على <code>player_id</code> في الرسالة المرسلة.\nيرجى"
        " التأكد من إرسال كود cURL أو Fetch محتوياً على آيدي اللاعب.",
    )

  return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
