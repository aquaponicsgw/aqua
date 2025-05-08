import feedparser
import os
import re
import html
import requests
from mastodon import Mastodon
from dotenv import load_dotenv
from flask import Flask

# Load environment variables from .env
load_dotenv()

ACCESS_TOKEN = os.getenv('MASTODON_ACCESS_TOKEN')
API_BASE_URL = os.getenv('MASTODON_API_BASE_URL')

# Validate required env vars
if not ACCESS_TOKEN or not API_BASE_URL:
    raise ValueError("MASTODON_ACCESS_TOKEN and MASTODON_API_BASE_URL must be set in the .env file")

# Initialize Mastodon
mastodon = Mastodon(
    access_token=ACCESS_TOKEN,
    api_base_url=API_BASE_URL
)

# RSS feeds to check
RSS_FEEDS = [
    "https://www.google.co.uk/alerts/feeds/18070038595192096982/3222385198977116976"
]

# File to store posted links
POSTED_LOG = "posted_links.txt"

# Load already posted links
if os.path.exists(POSTED_LOG):
    with open(POSTED_LOG, "r") as f:
        posted_links = set(f.read().splitlines())
else:
    posted_links = set()

def clean_html(raw_html):
    text = re.sub('<[^<]+?>', '', raw_html)
    return html.unescape(text)

def shorten_url_tinyurl(url):
    try:
        response = requests.get(f"https://tinyurl.com/api-create.php?url={url}")
        return response.text if response.status_code == 200 else url
    except:
        return url  # Fallback to original if error

new_posts = []

# Parse and post from each feed
for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        title = clean_html(entry.title)
        link = entry.link
        if link not in posted_links:
            short_link = shorten_url_tinyurl(link)
            status = f"{title}\n{short_link} #aquaponics"
            try:
                mastodon.toot(status)
                new_posts.append(link)
                print(f"Posted: {status}")
            except Exception as e:
                print(f"Failed to post: {status}\nError: {e}")

# Save new posted links
if new_posts:
    with open(POSTED_LOG, "a") as f:
        for link in new_posts:
            f.write(link + "\n")

# Flask app for HTTP access (required for Render to bind a port)
app = Flask(__name__)

@app.route('/')
def home():
    return "Aquaponics Mastodon Bot is running!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
