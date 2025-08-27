import pandas as pd
from utils_db import read_sql, to_sql

def compute_features():
    prices = read_sql("SELECT symbol, date, close, volume FROM prices")
    prices = prices.sort_values(["symbol","date"])

    def add_feats(g):
        g["ma_20"] = g["close"].rolling(20).mean()
        g["ma_50"] = g["close"].rolling(50).mean()
        delta = g["close"].diff()
        up = delta.clip(lower=0).rolling(14).mean()
        down = (-delta.clip(upper=0)).rolling(14).mean()
        rs = up / (down.replace(0, 1e-9))
        g["rsi_14"] = 100 - (100 / (1 + rs))
        return g

    feats = prices.groupby("symbol", group_keys=False).apply(add_feats)
    to_sql(feats, "features")
    return feats

if __name__ == "__main__":
    compute_features()
