import os
import requests
from flask import Flask, request, jsonify

BOT_TOKEN = "8967404868:AAFvirissJhm9Y3uDGkMd5WNEWDkmMViKfA"
MY_CHAT_ID = 6716126830
PORT = int(os.environ.get("PORT", 8080))

app_flask = Flask(__name__)
user_cookies = {}

def send_telegram_message(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": MY_CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            },
            timeout=10
        )
    except Exception as e:
        print(f"Telegram Error: {e}")

@app_flask.route('/webhook', methods=['POST'])
def webhook_receiver():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    cookie_str = data.get("cookie")
    target_link = data.get("link")
    
    if cookie_str and len(cookie_str) > 20:
        user_cookies[MY_CHAT_ID] = cookie_str
        
    if target_link and MY_CHAT_ID in user_cookies:
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://www.midasbuy.com/"
            }
            cookies_dict = {k.strip(): v.strip() for item in user_cookies[MY_CHAT_ID].split(';') if '=' in item for k, v in [item.split('=', 1)]}
            
            # تنفيذ الطلب الفعلي لسيرفرات ميداسباي
            response = requests.get(target_link, cookies=cookies_dict, headers=headers, timeout=15)
            
            send_telegram_message(
                f"🛡️ <b>STARK SYSTEM - LIVE EXECUTION</b>\n\n"
                f"✅ تم تنفيذ الرابط بنجاح!\n"
                f"🔗 <code>{target_link}</code>\n"
                f"📊 <b>حالة السيرفر:</b> {response.status_code}"
            )
            return jsonify({"status": "success", "code": response.status_code})
            
        except Exception as e:
            send_telegram_message(f"❌ خطأ أثناء تنفيذ الطلب: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
            
    return jsonify({"status": "stored", "message": "Data received successfully"})

@app_flask.route('/')
def home():
    return "Stark Bot Webhook Server is Running Live!"

if __name__ == '__main__':
    # تشغيل سيرفر فلاسك فقط بدون أي تداخل مع بولينج تيليجرام
    app_flask.run(host="0.0.0.0", port=PORT)
