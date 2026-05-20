import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


async def send_verification_email(to_email: str, token: str):
    subject = "Attendance Tracker - Verify Your Email"
    verification_link = f"http://localhost/verify?token={token}"

    html_content = f"""
    <html>
    <body>
        <h2>Welcome to Attendance Tracker</h2>
        <p>Please click the link below to verify your email:</p>
        <a href="{verification_link}" style="padding:10px 20px;background:#4F46E5;color:white;text-decoration:none;border-radius:5px;">
            Verify Email
        </a>
        <p>This link expires in 10 minutes.</p>
        <p>If you did not create an account, ignore this email.</p>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    msg.attach(MIMEText(html_content, "html"))

    await _send_email_async(msg, to_email)


async def _send_email_async(msg, to_email: str):
    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_USER, to_email, msg.as_string())
        server.quit()
    except Exception:
        raise
