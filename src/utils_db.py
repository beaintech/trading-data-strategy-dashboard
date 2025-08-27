# src/utils_db.py
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "market.sqlite"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def init_db():
    """Create tables if they don't exist"""
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS rss_news (
            id TEXT PRIMARY KEY,          -- guid or link
            symbol TEXT,
            source TEXT,
            title TEXT,
            link TEXT,
            published_utc TEXT,
            summary TEXT
        )
        """)
        conn.commit()

def insert_rss_entry(entry, symbol, source):
    """Insert one feed entry into rss_news"""
    from email.utils import parsedate_to_datetime

    guid = getattr(entry, "id", None) or getattr(entry, "guid", None) or entry.link
    pub = None
    if getattr(entry, "published", None):
        try:
            pub = parsedate_to_datetime(entry.published).astimezone().isoformat()
        except Exception:
            pub = None

    with get_conn() as conn:
        conn.execute("""
        INSERT OR IGNORE INTO rss_news (id, symbol, source, title, link, published_utc, summary)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            guid, symbol, source,
            entry.title, entry.link, pub,
            getattr(entry, "summary", None) or getattr(entry, "description", None)
        ))
        conn.commit()

def to_sql(df: pd.DataFrame, table: str):
    """Append DataFrame to table (auto-create if needed)"""
    with get_conn() as conn:
        df.to_sql(table, conn, if_exists="append", index=False)

def read_sql(query: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(
            query, conn,
            parse_dates=["date"] if "date" in query.lower() else None
        )
