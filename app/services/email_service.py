import httpx
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

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
            auth=("api", settings.MAILGUN_API_KEY),
            data={
                "from": settings.MAILGUN_FROM,
                "to": to_email,
                "subject": subject,
                "html": body,
            },
        )
        response.raise_for_status()
        print(f"[EMAIL] Sent OK to {to_email}")
