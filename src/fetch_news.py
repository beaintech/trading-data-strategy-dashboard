# src/fetch_news.py
import feedparser
import pandas as pd
from datetime import datetime, timezone
from utils_db import to_sql

def fetch_rss(feed_url, symbol=None, source="rss"):
    feed = feedparser.parse(feed_url)
    rows = []
    for e in feed.entries:
        rows.append({
            "published_at": pd.to_datetime(getattr(e, "published", getattr(e, "updated", datetime.now(timezone.utc)))),
            "published_at": pd.to_datetime(
                getattr(e, "published", getattr(e, "updated", datetime.now(timezone.utc)))
            ),
            "title": e.title,
            "sentiment_score": 0
        })
    df = pd.DataFrame(rows)
    feed = feedparser.parse("https://finance.yahoo.com/rss/headline?s=AAPL")
    print("Number of entries:", len(feed.entries))
    print(df.head())
    to_sql(df, "news")
    return df

if __name__ == "__main__":
    fetch_rss("https://finance.yahoo.com/rss/headline?s=AAPL", symbol="AAPL", source="YahooFinance") 