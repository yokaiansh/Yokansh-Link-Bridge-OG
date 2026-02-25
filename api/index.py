from flask import Flask, request
import telebot
import base64
import requests
import os
import time

# Initialize Flask and Bot
app = Flask(__name__)
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), threaded=False)

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
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
    link = m.text.strip()
    if "t.me" in link:
        enc = base64.b64encode(link.encode()).decode()
        v_token = int(time.time())
        # Clean the domain to prevent 404s
        domain = os.getenv("VERCEL_URL").replace("https://", "").replace("/", "").strip()
        bridge_url = f"https://{domain}/?target={enc}&v={v_token}"
        
        api_key = os.getenv("AROLINK_API")
        api_url = f"https://arolinks.com/api?api={api_key}&url={bridge_url}"
        
        try:
            res = requests.get(api_url).json()
            if res.get("status") == "success":
                bot.reply_to(m, f"✅ Secured Link:\n{res['shortenedUrl']}")
            else:
                bot.reply_to(m, "❌ Arolink API error.")
        except:
            bot.reply_to(m, "❌ Connection error.")

# ... all your bot handlers above ...

# Define both to ensure Vercel finds it
app = app

def handler(request):
    return app(request)
