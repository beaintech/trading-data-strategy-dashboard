def fetch_scalping_data(symbol="AAPL", period="5d", interval="1m"):
    data = yf.download(symbol, period=period, interval=interval)
    data.dropna(inplace=True)
    return data

def compute_scalping_signals(df, take_profit=0.003, stop_loss=-0.002):
    df["ma1"] = df["Close"].rolling(1).mean()
    df["ma5"] = df["Close"].rolling(5).mean()
    df["signal"] = 0
    df.loc[df["ma1"] > df["ma5"], "signal"] = 1
    df.loc[df["ma1"] < df["ma5"], "signal"] = -1
    return df

def backtest_scalping(df, take_profit=0.003, stop_loss=-0.002):
    trades = []
    pos = 0
    entry_price = 0
    for i, row in df.iterrows():
        if pos == 0 and row["signal"] != 0:
            pos = row["signal"]
            entry_price = row["Close"]
        elif pos != 0:
            change = (row["Close"] - entry_price) / entry_price * pos
            if change >= take_profit or change <= stop_loss:
                trades.append(change)
                pos = 0
                entry_price = 0
    return trades

import pandas as pd

def generate_signals(df, rsi_overbought=70, rsi_oversold=30):
    """
    Generate a short summary of signals for each ticker in df.
    Assumes df contains: Symbol, Date/Gmt time, Close, BB_UP, BB_LOW, RSI
    """
    summaries = []
    grouped = df.groupby("Symbol")  # in case df has multiple tickers

    for symbol, g in grouped:
        latest = g.iloc[-1]  # last row per ticker
        notes = []

        # Bollinger Band signals
        if pd.notna(latest["Close"]) and pd.notna(latest["BB_LOW"]) and latest["Close"] <= latest["BB_LOW"]:
            notes.append("Touching lower Bollinger Band")
        if pd.notna(latest["Close"]) and pd.notna(latest["BB_UP"]) and latest["Close"] >= latest["BB_UP"]:
            notes.append("Breaking upper Bollinger Band")

        # RSI signals
        if pd.notna(latest["RSI"]):
            if latest["RSI"] < rsi_oversold:
                notes.append("RSI oversold")
            elif latest["RSI"] > rsi_overbought:
                notes.append("RSI overbought")

        if not notes:
            notes.append("No major signals")

        summaries.append(f"{symbol} @ {latest['Date'] if 'Date' in latest else latest.name}: {', '.join(notes)}")

    return "\n".join(summaries)
