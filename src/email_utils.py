import smtplib
from email.mime.text import MIMEText

# 发送邮件函数 (直接写在 app.py)
def send_email(to_email, subject, body):
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = "beatrixyublome@gmail.com"
    SMTP_PASS = "rjko vwnd saat bugi"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        print(f"✅ Sent email to {to_email}")
        return True   # 👈 一定要返回 True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False  # 👈 出错时返回 False
