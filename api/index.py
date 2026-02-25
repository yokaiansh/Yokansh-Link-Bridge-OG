@bot.message_handler(func=lambda m: True)
def handle(m):
    link = m.text.strip() # Strip spaces from user input
    if "t.me" in link:
        enc = base64.b64encode(link.encode()).decode()
        v_token = int(time.time())
        
        # CLEAN URL LOGIC: Ensure no double slashes or extra symbols
        domain = os.getenv("VERCEL_URL").replace("https://", "").replace("http://", "").strip()
        bridge_url = f"https://{domain}/?target={enc}&v={v_token}"
        
        api_key = os.getenv("AROLINK_API").strip()
        api_url = f"https://arolinks.com/api?api={api_key}&url={bridge_url}"
        
        try:
            res = requests.get(api_url).json()
            if res.get("status") == "success":
                bot.reply_to(m, f"✅ **Secured Multi-Step Link:**\n\n{res['shortenedUrl']}")
            else:
                bot.reply_to(m, f"❌ Arolink Error: {res.get('message')}")
        except Exception as e:
            bot.reply_to(m, f"❌ System Error: {str(e)}")

# Replace 'app = app' with this function:
def handler(request):
    return app(request)
