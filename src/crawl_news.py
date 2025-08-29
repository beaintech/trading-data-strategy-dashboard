import feedparser
import pandas as pd
from utils_db import to_sql

def fetch_rss(feed_url, symbol=None, source="rss"):
    feed = feedparser.parse(feed_url)
    rows = []
    for e in feed.entries:
        rows.append({
            "source": source,
            "symbol": symbol,
            "published_at": pd.to_datetime(
                getattr(e, "published", getattr(e, "updated", None))
            ),
            "title": e.title,
            "url": e.link,
            "sentiment_score": None
        })
    df = pd.DataFrame(rows)
    to_sql(df, "news")
    return df

if __name__ == "__main__":
    df = fetch_rss("https://finance.yahoo.com/news/rss", symbol="AAPL")
    print(df.head())
