import os
import feedparser
from datetime import datetime

# output 폴더 생성
os.makedirs("output", exist_ok=True)

rss_url = "https://techcrunch.com/feed/"

feed = feedparser.parse(rss_url)

today = datetime.now().strftime("%Y_%m_%d")
filename = f"output/news_{today}.md"

with open(filename, "w", encoding="utf-8") as f:
    f.write(f"# TechCrunch AI/Tech News ({today})\n\n")

    for entry in feed.entries[:10]:
        f.write(f"## {entry.title}\n")
        f.write(f"{entry.link}\n\n")

print("News file generated:", filename)
