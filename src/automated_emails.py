import time
import schedule
from src.data_utils import fetch_prices
from app import run_email_job, generate_fake_users

# 股票列表
symbols = ["AAPL", "TSLA", "NVDA", "JNJ", "KO", "PG", "AMZN", "META", "NFLX"]

def job():
    print("📩 Running automated email job...")
    users_df = generate_fake_users(50) 
    data = fetch_prices(symbols, start="2024-01-01", interval="1d")
    run_email_job(users_df, data, symbols)

if __name__ == "__main__":
    print("📬 Automated email scheduler started...")

    # 每天早上 09:00 运行
    schedule.every().day.at("09:00").do(job)

    # 循环守护
    while True:
        schedule.run_pending()
        time.sleep(60)
