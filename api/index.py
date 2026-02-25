from flask import Flask, request
import telebot
import base64
import requests
import os

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), threaded=False)
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "Send a Telegram link to secure it!")

@bot.message_handler(func=lambda m: True)
def handle_link(m):
    link = m.text
    if "t.me" in link:
        enc = base64.b64encode(link.encode()).decode()
        dest = f"{os.getenv('VERCEL_URL')}?target={enc}"
        api_url = f"https://arolinks.com/api?api={os.getenv('AROLINK_API')}&url={dest}"
        res = requests.get(api_url).json()
        bot.reply_to(m, f"✅ Secured Arolink:\n{res['shortenedUrl']}")
    else:
        bot.reply_to(m, "Please send a valid t.me link.")

def handler(request):
    return app(request)
