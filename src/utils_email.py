import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def load_email_config(filename="email_config.txt"):
    config = {}
    with open(filename, "r") as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split("=", 1)
                config[key] = value.strip()
    return config

def send_email(subject, message, config):
    sender = config["sender_email"]
    password = config["sender_password"]
    receiver = config["receiver_email"]

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain", "utf-8"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
        print(f"✅ Email sent: {subject}")
    except Exception as e:
        print("❌ Email failed:", e)
