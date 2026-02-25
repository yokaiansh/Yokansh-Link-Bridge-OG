from flask import Flask, request
import telebot
import base64
import requests
import os

# Get these from your Vercel Environment Variables later
BOT_TOKEN = os.getenv("BOT_TOKEN")
AROLINK_API = os.getenv("AROLINK_API")
VERCEL_URL = os.getenv("VERCEL_URL") # e.g. https://my-project.vercel.app

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

@app.route('/api/index', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        return 'Error', 403

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Send me a Telegram link to create a Secured Arolink!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    link = message.text
    if "t.me" in link:
        # Encode the link for the bridge
        encoded = base64.b64encode(link.encode()).decode()
        bridge_link = f"{VERCEL_URL}?target={encoded}"
        
        # Call Arolink API
        api_url = f"https://arolinks.com/api?api={AROLINK_API}&url={bridge_link}"
        res = requests.get(api_url).json()
        
        if res.get("status") == "success":
            bot.reply_to(message, f"✅ **Secured Link:**\n`{res['shortenedUrl']}`")
        else:
            bot.reply_to(message, "❌ Arolink API Error.")
    else:
        bot.reply_to(message, "❌ Please send a valid t.me link.")

# For Vercel, the app must be accessible
def handler(request):
    return app(request)
