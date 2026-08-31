import json
import logging
import re
from flask import Flask, request
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# إعدادات البوت (حط توكن البوت بتاعك هنا)
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def process_midasbuy_request(player_id, user_id, token):
  """دالة تنفيذ طلب الميداسباي أوتوماتيك بالبيانات المستخرجة"""
  url = "https://pagedooapi.midasbuy.com/api/CallMpgo/osmidas/dd_prize_service/QueryPrizeInfoList"

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
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    return response.status_code, response.text
  except Exception as e:
    return 500, str(e)


@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
  data = request.get_json()
  if "message" in data and "text" in data["message"]:
    chat_id = data["message"]["chat"]["id"]
    text = data["message"]["text"]

    # لو المستخدم بعت كود أو بيانات، نقدر نستخرج منها المعرفات والتوكن
    # كمثال توضيحي: لو بعث رسالة تحتوي على بيانات الميداسباي
    if "midasbuy.com" in text or "player_id" in text:
      # استخراج الـ player_id والـ user_id باستخدام التعبيرات المنتظمة (Regex)
      player_id_match = re.search(r'"player_id"\s*:\s*"(\d+)"', text)
      user_id_match = re.search(r'"user_id"\s*:\s*"(\d+)"', text)

      if player_id_match and user_id_match:
        p_id = player_id_match.group(1)
        u_id = user_id_match.group(1)

        # توكن افتراضي أو مستخرج من نفس النص
        token = "146163c10927d20b2c0c970bc46d8b619b2dee969aad2913b87de992a6e242eb"

        status_code, resp_text = process_midasbuy_request(p_id, u_id, token)

        reply_msg = (
            f"✅ تم استلام الطلب وتشغيله بنجاح!\n- Player ID: {p_id}\n- Status"
            f" Code: {status_code}"
        )
      else:
        reply_msg = "❌ لم يتم العثور على المعرفات المطلوبة داخل النص المرسل."

      # إرسال الرد للتيليجرام
      requests.post(
          f"{TELEGRAM_API_URL}/sendMessage",
          json={"chat_id": chat_id, "text": reply_msg},
      )

  return "OK", 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)
