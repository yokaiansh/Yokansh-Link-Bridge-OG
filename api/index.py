import os
import time
import hashlib
import base64
import telebot
from flask import Flask, request

app = Flask(__name__)

# Pulling keys safely from Vercel Settings
TOKEN = os.getenv("BOT_TOKEN")
AROLINK_KEY = os.getenv("AROLINK_API")
SECRET_KEY = os.getenv("SECRET_KEY", "PRO_GLASS_BRIDGE_2026")
DOMAIN = os.getenv("VERCEL_URL", "your-project.vercel.app").replace("https://", "").replace("http://", "").strip("/")

bot = telebot.TeleBot(TOKEN, threaded=False)

@bot.message_handler(func=lambda m: True)
def handle(m):
    link = m.text.strip()
    if "t.me" in link:
        ts = str(int(time.time()))
        # Signature for security
        raw_sig = f"{link}{ts}{SECRET_KEY}"
        sig = hashlib.md5(raw_sig.encode()).hexdigest()
        enc_target = base64.b64encode(link.encode()).decode()
        
        # We add '&ak=' so the HTML knows your Arolinks Key
        bridge_url = f"https://{DOMAIN}/?target={enc_target}&ts={ts}&s={sig}&ak={AROLINK_KEY}"
        
        bot.reply_to(m, f"🛡️ **Secure Tunnel Generated**\n\n🔗 {bridge_url}")

app = app
