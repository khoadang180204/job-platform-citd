import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings


# SMTP Configuration
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "" # ĐIỀN MAIL CỦA APP PASSWORD
SMTP_APP_PASSWORD = "" # ĐIỀN APP PASSWORD VÀO ĐÂY

# Gửi email chứa mã OTP để đặt lại mật khẩu
def send_otp_email(to_email: str, otp_code: str) -> bool:
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f5f5; margin: 0; padding: 20px; }}
                .container {{ max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }}
                .header {{ background: linear-gradient(135deg, #00B14F 0%, #0f5f54 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ padding: 30px; text-align: center; }}
                .otp-box {{ background-color: #f8f9fa; border: 2px dashed #00B14F; border-radius: 10px; padding: 20px; margin: 25px 0; }}
                .otp-code {{ font-size: 36px; font-weight: bold; color: #00B14F; letter-spacing: 8px; margin: 0; }}
                .message {{ color: #666; font-size: 14px; line-height: 1.6; margin-bottom: 20px; }}
                .warning {{ color: #e74c3c; font-size: 13px; margin-top: 20px; }}
                .footer {{ background-color: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Đặt lại mật khẩu</h1>
                </div>
                <div class="content">
                    <p class="message">
                        Bạn vừa yêu cầu đặt lại mật khẩu cho tài khoản JobFAST của mình.<br>
                        Vui lòng sử dụng mã OTP bên dưới để xác nhận:
                    </p>
                    <div class="otp-box">
                        <p class="otp-code">{otp_code}</p>
                    </div>
                    <p class="message">
                        Mã này sẽ hết hạn sau <strong>10 phút</strong>.
                    </p>
                    <p class="warning">
                        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Tạo email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'[JobFAST] Mã OTP đặt lại mật khẩu: {otp_code}'
        msg['From'] = f'JobFAST <{SMTP_EMAIL}>'
        msg['To'] = to_email
        
        text_content = f"""
        ĐẶT LẠI MẬT KHẨU - JobFAST
        
        Mã OTP của bạn là: {otp_code}
        
        Mã này sẽ hết hạn sau 10 phút.
        
        Nếu bạn không yêu cầu đặt lại mật khẩu, vui lòng bỏ qua email này.
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Gửi email
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        
        print(f"Mã OTP đã được gửi đến {to_email}")
        return True
        
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gửi email: {e}")
        return False

# Gửi email thông báo mật khẩu đã được thay đổi
def send_password_changed_email(to_email: str) -> bool:
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f5f5; margin: 0; padding: 20px; }
                .container { max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); overflow: hidden; }
                .header { background: linear-gradient(135deg, #00B14F 0%, #0f5f54 100%); color: white; padding: 30px; text-align: center; }
                .header h1 { margin: 0; font-size: 24px; }
                .content { padding: 30px; text-align: center; }
                .success-icon { font-size: 48px; margin-bottom: 15px; }
                .message { color: #666; font-size: 14px; line-height: 1.6; }
                .footer { background-color: #f8f9fa; padding: 20px; text-align: center; color: #999; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Mật khẩu đã được thay đổi</h1>
                </div>
                <div class="content">
                    <p class="message">
                        Mật khẩu tài khoản JobFAST của bạn đã được thay đổi thành công.<br><br>
                        Nếu bạn không thực hiện thay đổi này, vui lòng liên hệ với chúng tôi ngay lập tức.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '[JobFAST] Mật khẩu của bạn đã được thay đổi'
        msg['From'] = f'JobFAST <{SMTP_EMAIL}>'
        msg['To'] = to_email
        
        text_content = """
        MẬT KHẨU ĐÃ ĐƯỢC THAY ĐỔI - JobFAST
        
        Mật khẩu tài khoản JobFAST của bạn đã được thay đổi thành công.
        
        Nếu bạn không thực hiện thay đổi này, vui lòng liên hệ với chúng tôi ngay lập tức.
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_APP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        
        print(f"Mã OTP đã được gửi đến {to_email}")
        return True
        
    except Exception as e:
        print(f"Đã xảy ra lỗi khi gửi email: {e}")
        return False
