from flask import Flask, request, make_response
import telebot
import base64
import requests
import os
import time

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), threaded=False)
app = Flask(__name__)

# This part kills the cache!
@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

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
    link = m.text
    if "t.me" in link:
        # 1. Base64 encode the destination
        enc = base64.b64encode(link.encode()).decode()
        
        # 2. Add a UNIQUE timestamp to bypass cache
        # This makes every link look different to the browser
        v_token = int(time.time())
        bridge_url = f"https://{os.getenv('VERCEL_URL')}?target={enc}&v={v_token}"
        
        # 3. Call Arolink API
        api_key = os.getenv("AROLINK_API")
        api_url = f"https://arolinks.com/api?api={api_key}&url={bridge_url}"
        
        try:
            res = requests.get(api_url).json()
            if res.get("status") == "success":
                bot.reply_to(m, f"✅ **Secured Multi-Step Link:**\n\n`{res['shortenedUrl']}`")
            else:
                bot.reply_to(m, "❌ Arolink API Error.")
        except Exception as e:
            bot.reply_to(m, f"❌ System Error: {str(e)}")
    else:
        bot.reply_to(m, "Please send a valid Telegram link!")

def handler(request):
    return app(request)
