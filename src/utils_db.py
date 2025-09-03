import sqlite3
import pandas as pd
from pathlib import Path
from email.utils import parsedate_to_datetime

# Database path
DB_PATH = Path(__file__).resolve().parents[1] / "db" / "market.sqlite"

def get_conn():
    """Ensure DB directory exists and return connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH, timeout=30)  # wait up to 30s if locked


def init_db():
    """Create tables if they don't exist"""
    with get_conn() as conn:
        # RSS News table
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
        # Prices table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            adj_close REAL,
            volume REAL,
            symbol TEXT
        )
        """)
        # Features (technical indicators) table
        conn.execute("""
        CREATE TABLE IF NOT EXISTS features (
            date TEXT,
            symbol TEXT,
            ema_fast REAL,
            ema_slow REAL,
            rsi REAL,
            atr REAL,
            bbm REAL,
            bbu REAL,
            bbl REAL,
            bbp REAL
        )
        """)
        conn.commit()


def insert_rss_entry(entry, symbol, source):
    """Insert one feed entry into rss_news"""
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
            guid,
            symbol,
            source,
            entry.title,
            entry.link,
            pub,
            getattr(entry, "summary", None) or getattr(entry, "description", None)
        ))
        conn.commit()


def to_sql(df: pd.DataFrame, table: str, if_exists="append"):
    with get_conn() as conn:
        # Explicit transaction control
        conn.execute("BEGIN")
        df.to_sql(table, conn, if_exists=if_exists, index=False)
        conn.commit()

def read_sql(query: str) -> pd.DataFrame:
    """Read SQL query result into DataFrame"""
    with get_conn() as conn:
        return pd.read_sql_query(
            query,
            conn,
            parse_dates=["date"] if "date" in query.lower() else None
        )
