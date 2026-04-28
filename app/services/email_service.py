import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from app.config import settings


async def send_otp_email(to_email: str, otp: str, purpose: str = "signup"):
    if purpose == "signup":
        subject = "Welcome to LMN8 - Verify Your Email"
        body = f"""<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;">
  <h2 style="color:#4f46e5;">Welcome to LMN8</h2>
  <p>Your verification code:</p>
  <p style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#111827;">{otp}</p>
  <p style="color:#9ca3af;font-size:12px;">Expires in 10 minutes.</p>
</div>"""
    else:
        subject = "LMN8 - Password Reset Code"
        body = f"""<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;">
  <h2 style="color:#4f46e5;">Reset Your Password</h2>
  <p>Your reset code:</p>
  <p style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#111827;">{otp}</p>
  <p style="color:#9ca3af;font-size:12px;">Expires in 10 minutes.</p>
</div>"""

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    # port 465 = direct SSL, port 587 = STARTTLS
    use_ssl = settings.SMTP_PORT == 465

    print(f"[EMAIL] {settings.SMTP_HOST}:{settings.SMTP_PORT} use_tls={use_ssl} → {to_email}")

    await asyncio.wait_for(
        aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASS,
            use_tls=use_ssl,
            start_tls=not use_ssl,
        ),
        timeout=20,
    )
    print(f"[EMAIL] Sent OK → {to_email}")
