from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    UserCreate, LoginRequest, OTPVerify,
    ForgotPasswordRequest, ResetPasswordRequest, TokenResponse
)
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.get("/admin/users", tags=["admin"])
async def get_all_users():
    from app.db.database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """
            SELECT u.id, u.email, u.is_verified, u.is_admin, u.created_at,
                   COUNT(DISTINCT s.id) as session_count,
                   COUNT(DISTINCT m.id) as message_count
            FROM auth_users u
            LEFT JOIN sessions s ON s.user_id = u.id
            LEFT JOIN messages m ON m.session_id = s.id
            GROUP BY u.id
            ORDER BY u.created_at DESC
            """
        )
    return {"users": [dict(r) for r in rows]}


@router.post("/signup", status_code=201)
async def signup(body: UserCreate):
    try:
        await auth_service.register_user(body.email, body.password)
        return {"message": "OTP sent to your email. Please verify to complete signup."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(body: OTPVerify):
    try:
        result = await auth_service.verify_signup_otp(body.email, body.code)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    try:
        result = await auth_service.login_user(body.email, body.password)
        return result
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest):
    await auth_service.forgot_password(body.email)
    return {"message": "If that email exists, a reset code has been sent."}


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest):
    try:
        await auth_service.reset_password(body.email, body.code, body.new_password)
        return {"message": "Password reset successfully."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
