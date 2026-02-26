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

# Automatically detect domain or fallback to your project name
DOMAIN = os.getenv("VERCEL_URL", "yokansh-link-bridge-og.vercel.app").replace("https://", "").replace("http://", "").strip("/")

bot = telebot.TeleBot(TOKEN, threaded=False)

# --- WEBHOOK ROUTE (CRITICAL FOR VERCEL) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK', 200
    return 'Forbidden', 403

# --- BOT LOGIC ---
@bot.message_handler(func=lambda m: True)
def handle(m):
    link = m.text.strip()
    
    # Check if user sent a Telegram link
    if "t.me" in link:
        if not AROLINK_KEY:
            bot.reply_to(m, "⚠️ Admin Error: AROLINK_API is not set in Vercel Variables.")
            return

        try:
            ts = str(int(time.time()))
            
            # Create a signature to prevent bypassing the glass bridge
            raw_sig = f"{link}{ts}{SECRET_KEY}"
            sig = hashlib.md5(raw_sig.encode()).hexdigest()
            
            # Encode target link for URL safety
            enc_target = base64.b64encode(link.encode()).decode()
            
            # Final URL including the Arolink API key for the HTML to use
            bridge_url = f"https://{DOMAIN}/?target={enc_target}&ts={ts}&s={sig}&ak={AROLINK_KEY}"
            
            bot.reply_to(m, f"🛡️ **Secure Tunnel Generated**\n\n🔗 {bridge_url}")
            
        except Exception as e:
            bot.reply_to(m, "❌ System Error. Check Vercel logs.")
    else:
        bot.reply_to(m, "👋 Please send a valid `t.me` link to encrypt it.")

# Required for Vercel
app = app
