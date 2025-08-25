# src/fetch_prices.py
import yfinance as yf
import pandas as pd
from utils_db import to_sql

def fetch_prices(symbols, start="2020-01-01"):
    frames = []
    for sym in symbols:
        df = yf.download(sym, start=start).reset_index()
        df["Symbol"] = sym
        df.rename(columns=str.lower, inplace=True)
        frames.append(df[["date","open","high","low","close","adj close","volume","Symbol"]])
    all_df = pd.concat(frames, ignore_index=True)
    all_df.rename(columns={"adj close":"adj_close","Symbol":"symbol"}, inplace=True)
    to_sql(all_df, "prices")
    return all_df

if __name__ == "__main__":
    fetch_prices(["AAPL","MSFT","NVDA","^GSPC"])
