import random
import string
from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from app.db.database import get_pool
from app.config import settings
from app.services.email_service import send_otp_email

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def create_access_token(user_id: str, email: str, is_admin: bool) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "is_admin": is_admin,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def _save_otp(email: str, purpose: str) -> str:
    code = _generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE auth_otp_codes SET used = TRUE WHERE email = $1 AND purpose = $2 AND used = FALSE",
            email, purpose
        )
        await conn.execute(
            "INSERT INTO auth_otp_codes (email, code, purpose, expires_at) VALUES ($1, $2, $3, $4)",
            email, code, purpose, expires_at
        )
    return code


async def _verify_otp(email: str, code: str, purpose: str) -> bool:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """SELECT id FROM auth_otp_codes
               WHERE email = $1 AND code = $2 AND purpose = $3
               AND used = FALSE AND expires_at > NOW()""",
            email, code, purpose
        )
        if not row:
            return False
        await conn.execute("UPDATE auth_otp_codes SET used = TRUE WHERE id = $1", row["id"])
        return True


async def register_user(email: str, password: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        existing = await conn.fetchrow("SELECT id, is_verified FROM auth_users WHERE email = $1", email)
        if existing:
            if existing["is_verified"]:
                raise ValueError("Email already registered")
            # Unverified user — update password and resend OTP
            hashed = pwd_context.hash(password)
            await conn.execute(
                "UPDATE auth_users SET hashed_password = $1 WHERE email = $2",
                hashed, email
            )
        else:
            hashed = pwd_context.hash(password)
            await conn.execute(
                "INSERT INTO auth_users (email, hashed_password) VALUES ($1, $2)",
                email, hashed
            )
    code = await _save_otp(email, "signup")
    await send_otp_email(email, code, purpose="signup")


async def verify_signup_otp(email: str, code: str) -> dict:
    if not await _verify_otp(email, code, "signup"):
        raise ValueError("Invalid or expired OTP")
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "UPDATE auth_users SET is_verified = TRUE WHERE email = $1 RETURNING id, email, is_admin",
            email
        )
        if not user:
            raise ValueError("User not found")
    return {"access_token": create_access_token(str(user["id"]), user["email"], user["is_admin"])}


async def login_user(email: str, password: str) -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, hashed_password, is_verified, is_admin FROM auth_users WHERE email = $1",
            email
        )
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise ValueError("Invalid credentials")
    if not user["is_verified"]:
        raise ValueError("Email not verified. Please check your email for the OTP.")
    return {"access_token": create_access_token(str(user["id"]), user["email"], user["is_admin"])}


async def forgot_password(email: str):
    pool = await get_pool()
    async with pool.acquire() as conn:
        user = await conn.fetchrow("SELECT id FROM auth_users WHERE email = $1", email)
    if not user:
        return  # Silently succeed to prevent email enumeration
    code = await _save_otp(email, "reset")
    await send_otp_email(email, code, purpose="reset")


async def reset_password(email: str, code: str, new_password: str):
    if not await _verify_otp(email, code, "reset"):
        raise ValueError("Invalid or expired OTP")
    hashed = pwd_context.hash(new_password)
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            "UPDATE auth_users SET hashed_password = $1 WHERE email = $2",
            hashed, email
        )
