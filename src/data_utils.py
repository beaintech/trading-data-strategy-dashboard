import yfinance as yf
import pandas as pd
import feedparser
from src.utils_db import to_sql
from datetime import datetime, timezone

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

    avg_gain = gain.ewm(alpha=1/rsi_period, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(alpha=1/rsi_period, min_periods=rsi_period).mean()

    rs = avg_gain / avg_loss.replace(0, 1e-9)
    df["RSI"] = 100 - (100 / (1 + rs))

    # ATR
    df["H-L"] = df["High"] - df["Low"]
    df["H-C"] = (df["High"] - df["Close"].shift()).abs()
    df["L-C"] = (df["Low"] - df["Close"].shift()).abs()
    df["TR"] = df[["H-L", "H-C", "L-C"]].max(axis=1)

    df["ATR"] = df["TR"].ewm(alpha=1/atr_period, min_periods=atr_period).mean()

    # Bollinger Bands
    bbm = df["Close"].rolling(bb_period).mean()
    bbb = df["Close"].rolling(bb_period).std().astype(float)
    bbu = bbm + bb_mult * bbb
    bbl = bbm - bb_mult * bbb
    df["BBM"] = bbm
    df["BBU"] = bbu
    df["BBL"] = bbl

    return df

def fetch_prices(symbols, start="2024-01-01", interval="1d"):
    """
    批量抓取行情数据 + 数据清理 + 指标计算
    """
    frames = []
    # 🔹 批量下载，支持多股票（高效）
    df_all = yf.download(symbols, start=start, interval=interval, group_by="ticker", threads=True)

    for sym in symbols:
        try:
            # 如果是多 symbol，取 df_all[sym]，否则就是单表
            df = df_all[sym].copy().reset_index() if len(symbols) > 1 else df_all.copy().reset_index()
        except Exception:
            print(f"⚠️ {sym} 数据获取失败，跳过")
            continue

        # 🔹 统一列名
        df.rename(columns={"Adj Close": "Adj_Close"}, inplace=True)

        # 🔹 核心数据清理步骤
        df = df.dropna()                           # 去掉 NaN 行
        df = df.drop_duplicates(subset=["Date"])   # 去掉重复日期
        df = df.reset_index(drop=True)             # 重置索引
        for col in ["Open", "High", "Low", "Close", "Adj_Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # 🔹 加指标
        df = compute_indicators(df)
        df["Symbol"] = sym
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)

def fetch_prices1(symbols, start="2024-01-01", interval="1d"):
    frames = []
    for sym in symbols:
        df = yf.download(sym, start=start, interval=interval)

        if df.empty:
            continue

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df.rename(columns={"Adj Close": "Adj_Close"}, inplace=True)

        for col in ["Open", "High", "Low", "Close", "Adj_Close", "Volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        df = compute_indicators(df)
        df["Symbol"] = sym
        frames.append(df)

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)

def fetch_rss(feed_url, symbol=None, source="rss"):
    feed = feedparser.parse(feed_url)
    rows = []
    for e in feed.entries:
        rows.append({
            "published_at": pd.to_datetime(
                getattr(e, "published", getattr(e, "updated", datetime.now(timezone.utc)))
            ),
            "title": e.title,
            "url": e.link,   # 👈 建议加上新闻链接
            "symbol": symbol,
            "source": source,
            "sentiment_score": 0   # 以后可以替换成 NLP 情感分数
        })
    
    df = pd.DataFrame(rows)

    # 打印调试信息
    print(f"✅ {symbol} - Fetched {len(df)} news entries")
    print(df.head())

    # 存入数据库
    if not df.empty:
        to_sql(df, "news")

    return df