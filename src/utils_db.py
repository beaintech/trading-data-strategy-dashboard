# src/utils_db.py
import sqlite3
import pandas as pd
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "db" / "market.sqlite"

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)

def to_sql(df: pd.DataFrame, table: str):
    with get_conn() as conn:
        df.to_sql(table, conn, if_exists="append", index=False)

def read_sql(query: str) -> pd.DataFrame:
    with get_conn() as conn:
        return pd.read_sql_query(query, conn, parse_dates=["date"] if "date" in query.lower() else None)
