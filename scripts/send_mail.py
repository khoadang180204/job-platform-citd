import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

EMAIL = "khoadang180204@gmail.com"
APP_PASSWORD = ""  # 16 ký tự

TO_EMAIL = "khoadang180204@gmail.com"

msg = MIMEText("Nếu bạn nhận được mail này thì token SMTP hoạt động OK 🎉")
msg["Subject"] = "Test SMTP Gmail"
msg["From"] = EMAIL
msg["To"] = TO_EMAIL

try:
    server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
    server.starttls()
    server.login(EMAIL, APP_PASSWORD)
    server.sendmail(EMAIL, TO_EMAIL, msg.as_string())
    server.quit()
    print("✅ SMTP OK – Mail đã gửi thành công")
except Exception as e:
    print("❌ SMTP FAILED:", e)
