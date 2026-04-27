import aiosmtplib
from email.mime.text import MIMEText
from app.config import settings


async def send_otp_email(to_email: str, otp: str, purpose: str = "signup"):
    if purpose == "signup":
        subject = "Welcome to LMN8 — Verify Your Email"
        body = f"""
<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f9fafb;border-radius:12px;">
  <h2 style="color:#4f46e5;margin-bottom:4px;">Welcome to LMN8</h2>
  <p style="color:#374151;margin-bottom:24px;">Thank you for signing up. Use the code below to verify your email address.</p>
  <div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:24px;text-align:center;margin-bottom:24px;">
    <p style="color:#6b7280;font-size:13px;margin:0 0 8px;">Your verification code</p>
    <p style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#111827;margin:0;">{otp}</p>
    <p style="color:#9ca3af;font-size:12px;margin:12px 0 0;">Expires in 10 minutes</p>
  </div>
  <p style="color:#6b7280;font-size:12px;">Do not share this code with anyone.</p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
  <p style="color:#9ca3af;font-size:11px;">If you never signed up for LMN8, you can safely ignore this email.</p>
</div>
"""
    else:
        subject = "LMN8 — Password Reset Code"
        body = f"""
<div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:32px;background:#f9fafb;border-radius:12px;">
  <h2 style="color:#4f46e5;margin-bottom:4px;">Reset Your Password</h2>
  <p style="color:#374151;margin-bottom:24px;">We received a request to reset your LMN8 password. Use the code below.</p>
  <div style="background:#fff;border:1px solid #e5e7eb;border-radius:8px;padding:24px;text-align:center;margin-bottom:24px;">
    <p style="color:#6b7280;font-size:13px;margin:0 0 8px;">Your reset code</p>
    <p style="font-size:36px;font-weight:bold;letter-spacing:8px;color:#111827;margin:0;">{otp}</p>
    <p style="color:#9ca3af;font-size:12px;margin:12px 0 0;">Expires in 10 minutes</p>
  </div>
  <p style="color:#6b7280;font-size:12px;">Do not share this code with anyone.</p>
  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0;">
  <p style="color:#9ca3af;font-size:11px;">If you didn't request a password reset, you can safely ignore this email.</p>
</div>
"""

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )
