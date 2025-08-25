import yfinance as yf
import pandas as pd
from utils_db import to_sql

def fetch_prices(symbols, start="2025-01-01"):
    frames = []
    for sym in symbols:
        df = yf.download(sym, start=start, auto_adjust=False).reset_index()
        df["symbol"] = sym
        df.rename(columns=str.lower, inplace=True)
        frames.append(df[["date","open","high","low","close","adj close","volume","symbol"]])
        print(df.columns)

    all_df = pd.concat(frames, ignore_index=True)
    to_sql(all_df, "prices")
    print(all_df.head()) 
    return all_df


if __name__ == "__main__":
    fetch_prices(["AAPL","MSFT","NVDA","^GSPC"])
