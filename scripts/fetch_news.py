"""Fetch recent fintech and crypto headlines from public RSS feeds and write news.json.

Runs in GitHub Actions on a schedule (see .github/workflows/news.yml).
Uses only the Python standard library. A feed that fails is skipped, and
news.json is left unchanged if every feed fails.
"""
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEEDS = {
    "fintech": [
        ("Finextra", "https://www.finextra.com/rss/headlines.aspx"),
        ("PYMNTS", "https://www.pymnts.com/feed/"),
        ("Payments Dive", "https://www.paymentsdive.com/feeds/news/"),
    ],
    "crypto": [
        ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("The Block", "https://www.theblock.co/rss.xml"),
        ("Cointelegraph", "https://cointelegraph.com/rss"),
    ],
}
PER_CATEGORY = 8
ATOM = "{http://www.w3.org/2005/Atom}"


def parse_date(text):
    if not text:
        return None
    text = text.strip()
    try:
        return parsedate_to_datetime(text)
    except (TypeError, ValueError):
        pass
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def fetch(source, url):
    req = urllib.request.Request(url, headers={"User-Agent": "card-tap-simulator-news/1.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        root = ET.fromstring(resp.read())
    items = []
    for it in root.iter("item"):  # RSS 2.0
        items.append((it.findtext("title"), it.findtext("link"), it.findtext("pubDate")))
    for it in root.iter(f"{ATOM}entry"):  # Atom
        link = it.find(f"{ATOM}link")
        items.append((it.findtext(f"{ATOM}title"), link.get("href") if link is not None else None,
                      it.findtext(f"{ATOM}updated") or it.findtext(f"{ATOM}published")))
    out = []
    for title, link, date in items:
        d = parse_date(date)
        if title and link and d:
            if d.tzinfo is None:
                d = d.replace(tzinfo=timezone.utc)
            out.append({"date": d, "title": " ".join(title.split()), "source": source, "url": link.strip()})
    return out


def main():
    result = {"updated": datetime.now(timezone.utc).date().isoformat()}
    any_ok = False
    for cat, feeds in FEEDS.items():
        collected = []
        for source, url in feeds:
            try:
                collected.extend(fetch(source, url))
                any_ok = True
            except Exception as e:  # keep going if one feed is down
                print(f"skip {source}: {e}", file=sys.stderr)
        seen, items = set(), []
        for n in sorted(collected, key=lambda x: x["date"], reverse=True):
            key = n["title"].lower()
            if key not in seen:
                seen.add(key)
                items.append({**n, "date": n["date"].date().isoformat()})
        result[cat] = items[:PER_CATEGORY]
    if not any_ok:
        print("every feed failed; leaving news.json unchanged", file=sys.stderr)
        return
    with open("news.json", "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
