from fetch_prices import fetch_prices
from signals import generate_signals
from email.mime.text import MIMEText
import smtplib

def send_email(summary_text):
    SMTP_HOST = "smtp.example.com"
    SMTP_PORT = 587
    SMTP_USER = "you@example.com"
    SMTP_PASS = "your_app_password"

    msg = MIMEText(summary_text, "plain", "utf-8")
    msg["Subject"] = "Daily Trading Signals"
    msg["From"] = SMTP_USER
    msg["To"] = "recipient@example.com"

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

if __name__ == "__main__":
    # 1. fetch latest data
    df = fetch_prices(["EURUSD=X","AAPL","MSFT"], interval="5m", start="2024-01-01")

    # 2. generate trading signals (scalping logic)
    summary_text = generate_signals(df)

    # 3. send signals by email
    send_email(summary_text)
    print("✅ Email sent")
