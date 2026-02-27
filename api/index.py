import os
import time
import hashlib
import base64
import telebot
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
AROLINK_KEY = os.getenv("AROLINK_API")
SECRET_KEY = os.getenv("SECRET_KEY", "PRO_GLASS_BRIDGE_2026")

# Vercel-specific domain detection
DOMAIN = os.getenv("VERCEL_URL", "yokansh-link-bridge-og.vercel.app").replace("https://", "").replace("http://", "").strip("/")

# CRITICAL: threaded=False is mandatory for Vercel/Serverless
bot = telebot.TeleBot(TOKEN, threaded=False)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        try:
            json_string = request.get_data().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return 'OK', 200
        except Exception as e:
            print(f"Webhook Error: {e}")
            return 'Error', 500
    return 'Forbidden', 403

@bot.message_handler(func=lambda m: True)
def handle(m):
    try:
        link = m.text.strip()
        if "t.me" in link:
            if not AROLINK_KEY:
                bot.reply_to(m, "⚠️ Configuration Error: AROLINK_API missing.")
                return

            ts = str(int(time.time()))
            raw_sig = f"{link}{ts}{SECRET_KEY}"
            sig = hashlib.md5(raw_sig.encode()).hexdigest()
            enc_target = base64.b64encode(link.encode()).decode()
            
            bridge_url = f"https://{DOMAIN}/?target={enc_target}&ts={ts}&s={sig}&ak={AROLINK_KEY}"
            
            bot.reply_to(m, f"🛡️ **Secure Tunnel Generated**\n\n🔗 {bridge_url}", parse_mode="Markdown")
        else:
            bot.reply_to(m, "👋 Please send a valid `t.me` link.")
    except Exception as e:
        print(f"Logic Error: {e}")

# Entry point for Vercel
app = app
