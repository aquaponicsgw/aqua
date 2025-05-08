import os
import time
import feedparser
from mastodon import Mastodon
from flask import Flask
from threading import Thread
from dotenv import load_dotenv

# === Load environment variables from .env ===
load_dotenv()
ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
API_BASE_URL = os.getenv("MASTODON_API_BASE_URL")

# === Connect to Mastodon API ===
mastodon = Mastodon(access_token=ACCESS_TOKEN, api_base_url=API_BASE_URL)

# === RSS Feed URL (customize this) ===
RSS_FEED_URL = "https://www.google.co.uk/alerts/feeds/18070038595192096982/3222385198977116976"

# === Track posted items ===
POSTED_LOG = "posted.txt"
if os.path.exists(POSTED_LOG):
    with open(POSTED_LOG, "r") as f:
        posted_links = set(f.read().splitlines())
else:
    posted_links = set()

# === Bot: check feed and post ===
def check_and_post():
    global posted_links
    feed = feedparser.parse(RSS_FEED_URL)
    for entry in feed.entries:
        if entry.link not in posted_links:
            status = f"{entry.title}\n{entry.link} #aquaponics"
            try:
                mastodon.status_post(status)
                print(f"✅ Posted: {status}")
                posted_links.add(entry.link)
                with open(POSTED_LOG, "a") as f:
                    f.write(entry.link + "\n")
            except Exception as e:
                print(f"❌ Error posting: {e}")

# === Loop to check RSS feed every 5 mins ===
def run_bot():
    while True:
        check_and_post()
        time.sleep(300)

# === Flask web server for uptime pings ===
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Aquaponics Mastodon Bot is running."

def start_flask():
    port = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=port)

# === Start both bot and web server ===
if __name__ == "__main__":
    Thread(target=run_bot).start()
    start_flask()
