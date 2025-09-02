import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from utils_email import load_email_config, send_email

try:
    # 下載數據（1分鐘頻率，演示剝頭皮）
    data = yf.download("AAPL", period="5d", interval="1m")
    data.dropna(inplace=True)

    # 計算超短期均線
    data["ma1"] = data["Close"].rolling(1).mean()
    data["ma5"] = data["Close"].rolling(5).mean()

    # 策略參數
    take_profit = 0.001   # 0.1%
    stop_loss   = -0.001  # -0.1%

    # 信號：當 MA1 上穿 MA5 → 開多；下穿 → 開空
    data["signal"] = 0
    data.loc[data["ma1"] > data["ma5"], "signal"] = 1   # 多
    data.loc[data["ma1"] < data["ma5"], "signal"] = -1  # 空
    print(data[["Close", "ma1", "ma5", "signal"]].head(20))  # 检查

    # EMA crossover
    data["ema10"] = data["Close"].ewm(span=10, adjust=False).mean()
    data["ema50"] = data["Close"].ewm(span=50, adjust=False).mean()

    data["signal"] = 0
    data.loc[data["ema10"] > data["ema50"], "signal"] = 1
    data.loc[data["ema10"] < data["ema50"], "signal"] = -1

    print(data.tail(20))

    # 計算收益
    data["ret"] = data["Close"].pct_change().fillna(0)

    # 模擬持倉（前一根信號）
    data["position"] = data["signal"].shift(1).fillna(0)

    # 計算策略收益
    data["strategy_ret"] = data["position"] * data["ret"]

    # 加入止盈止損（簡化：判斷單筆交易）
    # 初始化
    trades = []
    pos = 0
    entry_price = 0

    # 載入郵件設定
    config = load_email_config()

    # 回測循環
    for row in data.itertuples(index=True):
        # 開倉
        if pos == 0 and row.signal != 0:
            pos = row.signal
            entry_price = row.Close

            subject = "📈 New Trade Opened"
            message = f"Signal: {pos}\nEntry Price: {entry_price}\nTime: {row.Index}"
            send_email(subject, message, config)

        # 持倉
        elif pos != 0:
            change = (row.Close - entry_price) / entry_price * pos
            if change >= take_profit or change <= stop_loss:
                # 強制平倉：如果最後還有持倉，按最後收盤價平倉
                if pos != 0:
                    change = (data["Close"].iloc[-1] - entry_price) / entry_price * pos
                    trades.append(change)

                subject = "📉 Trade Closed"
                message = f"Exit Price: {row.Close}\nPnL: {change:.2%}\nTime: {row.Index}"
                send_email(subject, message, config)

                pos = 0
                entry_price = 0
finally:
    # 結果統計
    total_ret = np.sum(trades)
    win_rate = np.mean([1 if x > 0 else 0 for x in trades]) if trades else 0

    print(f"Anzahl der Trades: {len(trades)}")
    print(f"Gesamtrendite: {total_ret:.2%}")
    print(f"Trefferquote: {win_rate:.2%}")

# 繪製曲線
(data["strategy_ret"].cumsum()+1).plot(figsize=(12,6), label="Scalping Strategy")
(data["ret"].cumsum()+1).plot(label="Buy & Hold")
plt.legend()
plt.title("Scalping Strategy Backtest (AAPL 1min)")
plt.show()