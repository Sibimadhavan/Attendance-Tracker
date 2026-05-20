import re
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from app.database import db, redis_client
from app.utils.auth import hash_password, verify_password, generate_uuid, generate_token
from app.utils.email import send_verification_email
from app.utils.dependencies import get_current_user
from app.config import SESSION_EXPIRE, VERIFICATION_EXPIRE

logger = logging.getLogger(__name__)
security = HTTPBearer()

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Name is required")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters")
        if len(v) > 50:
            raise ValueError("Name must not exceed 50 characters")
        if not re.match(r"^[a-zA-Z\s\-'.]+$", v):
            raise ValueError("Name can only contain letters, spaces, hyphens, and apostrophes")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if len(v) > 100:
            raise ValueError("Password must not exceed 100 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyRequest(BaseModel):
    token: str


@router.post("/register")
async def register(data: RegisterRequest):
    existing = await db.users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    user_id = generate_uuid()
    hashed = hash_password(data.password)

    token = generate_token()
    await redis_client.setex(f"verification:{token}", VERIFICATION_EXPIRE, user_id)

    try:
        await send_verification_email(data.email, token)
    except Exception:
        await redis_client.delete(f"verification:{token}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email. Please try again later."
        )

    await db.users.insert_one({
        "user_id": user_id,
        "name": data.name,
        "email": data.email,
        "password": hashed,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    })

    return {"message": "Registration successful. Please check your email to verify.", "user_id": user_id}


@router.post("/verify")
async def verify_email(data: VerifyRequest):
    user_id = await redis_client.get(f"verification:{data.token}")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

    user = await db.users.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User not found")

    if user["is_verified"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already verified")

    await db.users.update_one(
        {"user_id": user_id},
        {"$set": {"is_verified": True, "updated_at": datetime.utcnow()}}
    )

    await redis_client.delete(f"verification:{data.token}")

    return {"message": "Email verified successfully"}


@router.post("/login")
async def login(data: LoginRequest):
    user = await db.users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user["is_verified"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Please verify your email before logging in")

    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    session_token = generate_token()
    await redis_client.setex(f"session:{session_token}", SESSION_EXPIRE, user["user_id"])

    return {
        "message": "Login successful",
        "token": session_token,
        "user": {
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
        },
    }


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    await redis_client.delete(f"session:{token}")
    return {"message": "Logged out successfully"}
