# src/backtest.py
import pandas as pd
from utils_db import read_sql

def ma_crossover_return():
    df = read_sql("""
      SELECT f.symbol, f.date, f.ma_20, f.ma_50, p.close
      FROM features f
      JOIN prices p ON f.symbol=p.symbol AND f.date=p.date
      ORDER BY f.symbol, f.date
    """)
    df["signal"] = (df["ma_20"] > df["ma_50"]).astype(int)
    df["ret"] = df.groupby("symbol")["close"].pct_change().fillna(0)
    df["strategy_ret"] = df["signal"].shift(1).fillna(0) * df["ret"]
    perf = df.groupby("symbol")[["ret","strategy_ret"]].sum().reset_index()
    return perf

if __name__ == "__main__":
    print(ma_crossover_return())
