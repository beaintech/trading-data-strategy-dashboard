import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def compute_indicators(df, ema_fast=10, ema_slow=20,
                       rsi_period=14, bb_period=15, bb_mult=1.5,
                       atr_period=14):
    if df.empty:
        return df

    # EMA
    df["EMA_fast"] = df["Close"].ewm(span=ema_fast, adjust=False).mean()
    df["EMA_slow"] = df["Close"].ewm(span=ema_slow, adjust=False).mean()

    # RSI
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ATR
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = abs(df["High"] - df["Close"].shift(1))
    df["L-C"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-C", "L-C"]].max(axis=1)
    df["ATR"] = df["TR"].rolling(atr_period).mean()

    # Bollinger Bands
    bbm = df["Close"].rolling(bb_period).mean()
    bbb = df["Close"].rolling(bb_period).std().astype(float)
    bbu = bbm + bb_mult * bbb
    bbl = bbm - bb_mult * bbb
    df["BBM"] = bbm
    df["BBU"] = bbu
    df["BBL"] = bbl

    return df

def fetch_prices(symbols, start="2024-05-01", interval="1d"):
    frames = []
    for sym in symbols:
        print(f"⬇️ Downloading {sym} ...")
        df = yf.download(sym, start=start, interval=interval)

        if df.empty:
            print(f"⚠️ {sym} 无数据，跳过")
            continue

        # 如果是多重索引，展开
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df.rename(columns={"Adj Close": "Adj_Close"}, inplace=True)

        # 确保数值列是 float
        for col in ["Open", "High", "Low", "Close", "Adj_Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = compute_indicators(df)
        df["Symbol"] = sym
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    all_df = pd.concat(frames, ignore_index=True)
    return all_df

# 🔎 测试
symbols = ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"]
data = fetch_prices(symbols, start="2024-01-01", interval="1d")
print(data.tail())
