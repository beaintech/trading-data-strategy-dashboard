from src.data_utils import fetch_prices
import schedule, time
from datetime import datetime

def job():
    symbols = ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"]
    df = fetch_prices(symbols, start="2024-01-01", interval="1d")
    df.to_csv("db/latest_prices.csv", index=False)
    print(f"✅ Updated {len(df)} rows at {datetime.now()}")

if __name__ == "__main__":
    # 启动时立即更新一次
    job()

    # 每天早上 9 点自动跑
    schedule.every().day.at("18:36").do(job)

    # 守护进程
    while True:
        schedule.run_pending()
        time.sleep(60)