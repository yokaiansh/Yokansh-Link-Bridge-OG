import os
import time
import hashlib
import base64
import telebot
from flask import Flask, request

app = Flask(__name__)

# --- CONFIGURATION ---
TOKEN = os.getenv("BOT_TOKEN")
# This must match the Secret Key in your HTML file below
SECRET_KEY = "PRO_GLASS_BRIDGE_2026" 
DOMAIN = os.getenv("VERCEL_URL", "your-project.vercel.app").replace("https://", "").replace("http://", "").strip("/")

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
            # 1. Create a Timestamp (Link valid for 10 mins)
            ts = str(int(time.time()))
            
            # 2. Generate Security Signature to prevent bypassing
            raw_sig = f"{link}{ts}{SECRET_KEY}"
            sig = hashlib.md5(raw_sig.encode()).hexdigest()
            
            # 3. Base64 encode the TG link
            enc_target = base64.b64encode(link.encode()).decode()
            
            # 4. Generate the Bridge URL
            bridge_url = f"https://{DOMAIN}/?target={enc_target}&ts={ts}&s={sig}"
            
            msg = (
                "🛡️ **Link Secured**\n\n"
                "Your destination is ready. Click below to start the 2-step verification:\n\n"
                f"🔗 {bridge_url}"
            )
            bot.reply_to(m, msg, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(m, "❌ System busy. Please try again.")

app = app
