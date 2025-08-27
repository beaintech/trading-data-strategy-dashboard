# import yfinance as yf
# import pandas as pd
# from utils_db import to_sql

# def fetch_prices(symbols, start="2025-01-01"):
#     frames = []
#     for sym in symbols:
#         df = yf.download(sym, start=start, auto_adjust=False).reset_index()
#         df["symbol"] = sym
#         df.rename(columns=str.lower, inplace=True)
#         frames.append(df[["date","open","high","low","close","adj close","volume","symbol"]])
#         print(df.columns)

#     all_df = pd.concat(frames, ignore_index=True)
#     to_sql(all_df, "prices")
#     print(all_df.head()) 
#     return all_df


# if __name__ == "__main__":
#     fetch_prices(["AAPL","MSFT","NVDA","^GSPC"])

# src/fetch_prices.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from utils_db import to_sql


def compute_indicators(df, ema_fast=10, ema_slow=20,
                       rsi_period=14, bb_period=15, bb_mult=1.5,
                       atr_period=14):
    if df.empty:
        return df  # 如果數據是空的，直接返回

    # ========== EMA ==========
    df["EMA_fast"] = df["Close"].ewm(span=ema_fast, adjust=False).mean()
    df["EMA_slow"] = df["Close"].ewm(span=ema_slow, adjust=False).mean()

    # ========== RSI ==========
    delta = df["Close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(rsi_period).mean()
    avg_loss = loss.rolling(rsi_period).mean()
    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ========== ATR ==========
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = abs(df["High"] - df["Close"].shift(1))
    df["L-C"] = abs(df["Low"] - df["Close"].shift(1))
    df["TR"] = df[["H-L", "H-C", "L-C"]].max(axis=1)
    df["ATR"] = df["TR"].rolling(atr_period).mean()

    # ========== Bollinger Bands ==========
    bbm = df["Close"].rolling(bb_period).mean()
    bbb = df["Close"].rolling(bb_period).std().astype(float)
    bbu = bbm + bb_mult * bbb
    bbl = bbm - bb_mult * bbb

    df["BBM_15_1.5"] = bbm
    df["BBB_15_1.5"] = bbb
    df["BBU_15_1.5"] = bbu
    df["BBL_15_1.5"] = bbl
    df["BBP_15_1.5"] = (df["Close"] - bbl) / (bbu - bbl).replace(0, 1e-9)

    return df



def adjust_start_for_interval(start, interval):
    """
    根據 interval 自動調整可用的最早時間
    """
    now = datetime.now()
    if interval == "5m":
        # Yahoo Finance 限制：5 分鐘數據只能取最近 60 天
        earliest = now - timedelta(days=59)
    elif interval == "1h":
        # 1 小時數據大約能取最近 2 年
        earliest = now - timedelta(days=730)
    else:
        # 日線及以上，可以取更久
        earliest = datetime(2000, 1, 1)

    start_dt = datetime.strptime(start, "%Y-%m-%d")
    return max(start_dt, earliest).strftime("%Y-%m-%d")


def fetch_prices(symbols, start="2020-01-01", interval="1h"):
    """
    抓取行情數據 + 技術指標，並寫入 SQLite
    """
    frames = []
    start = adjust_start_for_interval(start, interval)

    for sym in symbols:
        print(f"Downloading {sym} from {start} with interval={interval}...")
        df = yf.download(sym, start=start, interval=interval).reset_index()

        if df.empty:
            print(f"⚠️ {sym} 無法獲取數據，跳過")
            continue

        # 保證欄位標準化
        df.rename(columns={"Datetime": "Date", "Adj Close": "Adj_Close"}, inplace=True)

        # 計算技術指標
        df = compute_indicators(df)

        df["Symbol"] = sym
        frames.append(df)

    if not frames:
        print("❌ 沒有任何數據下載成功")
        return pd.DataFrame()

    all_df = pd.concat(frames, ignore_index=True)
    to_sql(all_df, "prices_with_indicators")
    return all_df


if __name__ == "__main__":
    # 測試：EUR/USD 5 分鐘數據（自動限制為最近 60 天）
    data = fetch_prices(["EURUSD=X"], start="2025-01-01", interval="5m")
    print(data.tail())
