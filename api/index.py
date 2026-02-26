import os
import time
import base64
import requests
import telebot
from flask import Flask, request

app = Flask(__name__)

# Load variables safely
TOKEN = os.getenv("BOT_TOKEN")
AROLINK_KEY = os.getenv("AROLINK_API")
# Use a fallback if VERCEL_URL is missing
DOMAIN = os.getenv("VERCEL_URL", "yokansh-link-bridge-og.vercel.app").replace("https://", "").replace("http://", "").strip("/")

bot = telebot.TeleBot(TOKEN, threaded=False)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

@bot.message_handler(func=lambda m: True)
def handle(m):
    link = m.text.strip()
    if "t.me" in link:
        try:
            # The line that was likely crashing (missing base64/time)
            enc = base64.b64encode(link.encode()).decode()
            v_token = int(time.time())
            
            bridge_url = f"https://{DOMAIN}/?target={enc}&v={v_token}"
            api_url = f"https://arolinks.com/api?api={AROLINK_KEY}&url={bridge_url}"
            
            res = requests.get(api_url).json()
            if res.get("status") == "success":
                bot.reply_to(m, f"✅ **Secured Link:**\n\n{res['shortenedUrl']}")
            else:
                bot.reply_to(m, f"❌ API Error: {res.get('message')}")
        except Exception as e:
            bot.reply_to(m, f"❌ System Error: {str(e)}")
    else:
        bot.reply_to(m, "Please send a valid t.me link.")

# Final export for Vercel
app = app
