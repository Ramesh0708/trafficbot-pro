#!/usr/bin/env python3

"""
TrafficBot Pro – CLI version for GitHub Actions
Automated multi-city traffic alerts with:
- RSS feeds
- Severity markers
- Smart summary
- Rotating fun facts
- Live traffic map
- Optional YouTube creator promotion
"""

import os
import requests
import feedparser
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime

# ---------------- CONFIG ---------------- #

CITY = os.getenv("CITY", "Pune")
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

# Maps centering (default = Pune Baner)
CITY_MAPS = {
    "pune": "https://www.google.com/maps/@18.5590,73.7799,15z/data=!5m1!1e1",
    "mumbai": "https://www.google.com/maps/@19.0760,72.8777,14z/data=!5m1!1e1",
    "bangalore": "https://www.google.com/maps/@12.9716,77.5946,14z/data=!5m1!1e1",
    "delhi": "https://www.google.com/maps/@28.6139,77.2090,14z/data=!5m1!1e1",
}
LIVE_MAP = CITY_MAPS.get(CITY.lower(), CITY_MAPS["pune"])

RSS_FEEDS = [
    f"https://news.google.com/rss/search?q={CITY}+Traffic&hl=en-IN&gl=IN&ceid=IN:en",
]

MAX_ARTICLES = 5
HOURS_FRESH = 24

# Rotating fun facts
FACTS = [
    "Pune has more two-wheelers than any Indian city.",
    "Balewadi High Street traffic peaks after 7 PM.",
    "Hinjewadi sees Monday morning surges.",
    "University Circle handles 1.2 lakh vehicles daily.",
    "Illegal parking causes micro-jams in most cities."
]

# ---------------- HELPERS ---------------- #

def parse_datetime(entry):
    for field in ("published", "updated", "pubDate"):
        ts = entry.get(field)
        if ts:
            try:
                dt = parsedate_to_datetime(ts)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt.astimezone(timezone.utc)
            except Exception:
                pass
    return None


def severity(title):
    text = title.lower()
    if any(w in text for w in ["accident", "crash", "blocked", "jam", "closed"]):
        return "🔴"
    if any(w in text for w in ["slow", "delay", "snarl", "heavy"]):
        return "🟡"
    return "🟢"


def fetch_news():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOURS_FRESH)
    articles = []

    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            dt = parse_datetime(entry) or datetime.now(timezone.utc)
            if dt < cutoff:
                continue

            articles.append({
                "title": entry.title,
                "link": entry.link,
                "published": dt,
            })

    articles.sort(key=lambda x: x["published"], reverse=True)
    return articles


def generate_summary(titles):
    text = " ".join(t.lower() for t in titles)

    if "accident" in text:
        return "🔍 Summary: Accident reported — expect delays."
    if "baner" in text or "balewadi" in text:
        return f"🔍 Summary: Moderate congestion around {CITY} hotspots."
    if "metro" in text or "work" in text:
        return "🔍 Summary: Roadwork/metro activity slowing traffic."

    return "🔍 Summary: No major bottlenecks reported."


def rotate_fact():
    idx = datetime.now().day % len(FACTS)
    return f"💡 Fact: {FACTS[idx]}"


# ---------------- MESSAGE BUILDER ---------------- #

def build_message(articles):
    timestamp = datetime.now().strftime("%d %b %Y • %I:%M %p")

    header = f"🚦 TrafficBot Pro • {CITY.title()} • {timestamp}\n\n"

    if not articles:
        return (
            f"{header}"
            "🟢 No major updates found.\n\n"
            f"{generate_summary([])}\n\n"
            f"🗺️ Live Traffic Map: {LIVE_MAP}\n\n"
            f"{rotate_fact()}"
        )

    lines = []
    titles = []
    for a in articles[:MAX_ARTICLES]:
        sev = severity(a["title"])
        lines.append(f"• {sev} [{a['title']}]({a['link']})")
        titles.append(a["title"])

    extra = ""
    if len(articles) > MAX_ARTICLES:
        extra = f"\n\n… and {len(articles) - MAX_ARTICLES} more updates."

    summary = generate_summary(titles)

    return (
        f"{header}"
        + "\n".join(lines)
        + extra
        + f"\n\n{summary}"
        + f"\n\n🗺️ Live Traffic Map: {LIVE_MAP}"
        + f"\n\n{rotate_fact()}"
    )

# ---------------- TEAMS POST ---------------- #

def send_to_teams(text):
    if not TEAMS_WEBHOOK_URL:
        print("❗ TEAMS_WEBHOOK_URL missing — printing output instead:\n")
        print(text)
        return

    payload = {"text": text.replace("\n", "\n\n")}
    try:
        requests.post(TEAMS_WEBHOOK_URL, json=payload, timeout=10)
        print("✔ Posted to Teams")
    except Exception as e:
        print("❗ Error posting:", e)


# ---------------- MAIN ---------------- #

def main():
    articles = fetch_news()
    msg = build_message(articles)
    send_to_teams(msg)


if __name__ == "__main__":
    main()

