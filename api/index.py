import os
import time
import base64
import requests
import telebot
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
AROLINK_KEY = os.getenv("AROLINK_API")
# Replace with your actual Vercel domain if the env variable isn't set
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
            # STEP 1: Create the Vercel Bridge URL
            # We encode the target link so it's safe in the URL
            enc_target = base64.b64encode(link.encode()).decode()
            bridge_url = f"https://{DOMAIN}/?target={enc_target}"
            
            # STEP 2: Shorten the Bridge URL via Arolinks
            # This ensures Arolinks is the 'entry point' for the user
            api_url = f"https://arolinks.com/api?api={AROLINK_KEY}&url={bridge_url}"
            
            response = requests.get(api_url).json()
            
            if response.get("status") == "success":
                short_url = response.get("shortenedUrl")
                msg = (
                    "🛡️ **Security Gateway Active**\n\n"
                    "Your link has been processed through our secure tunnel. "
                    "Click below to begin verification:\n\n"
                    f"🔗 {short_url}"
                )
                bot.reply_to(m, msg, parse_mode="Markdown")
            else:
                bot.reply_to(m, "❌ API Error: Could not generate short link.")
                
        except Exception as e:
            bot.reply_to(m, f"❌ System Error: {str(e)}")
    else:
        bot.reply_to(m, "👋 Send me a Telegram (t.me) link to secure it!")

# Vercel Entry Point
app = app
