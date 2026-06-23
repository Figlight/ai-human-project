import base64
import json
import hmac
import time
import secrets
import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.database import get_db, async_session
from backend.app.db.models import User
from backend.app.models.schemas import ApiResponse
from backend.config import settings

router = APIRouter()
security = HTTPBearer()


# Pydantic schemas for auth
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=50)
    role: str = Field("user", description="user or admin")


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    username: str
    role: str


class UserInfo(BaseModel):
    id: int
    username: str
    role: str


# JWT signature and verification helper functions
def create_jwt(payload: dict, expires_in: int = 1800) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = payload.copy()
    payload["exp"] = int(time.time()) + expires_in
    
    header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode("utf-8")).decode("utf-8").rstrip("=")
    payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8").rstrip("=")
    
    secret_key = getattr(settings, "JWT_SECRET_KEY", "景区导览AI数字人-默认JWT签名密钥-2026")
    signature = hmac.new(
        secret_key.encode("utf-8"),
        f"{header_b64}.{payload_b64}".encode("utf-8"),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("utf-8").rstrip("=")
    
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_jwt(token: str) -> dict | None:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        
        # Verify signature
        secret_key = getattr(settings, "JWT_SECRET_KEY", "景区导览AI数字人-默认JWT签名密钥-2026")
        expected_sig = hmac.new(
            secret_key.encode("utf-8"),
            f"{header_b64}.{payload_b64}".encode("utf-8"),
            hashlib.sha256
        ).digest()
        
        # Base64 padding normalization
        def pad_b64(b64_str: str) -> str:
            rem = len(b64_str) % 4
            if rem:
                b64_str += "=" * (4 - rem)
            return b64_str
            
        expected_sig_b64 = base64.urlsafe_b64encode(expected_sig).decode("utf-8").rstrip("=")
        
        if not hmac.compare_digest(signature_b64, expected_sig_b64):
            return None
            
        # Decode payload
        payload_data = json.loads(base64.urlsafe_b64decode(pad_b64(payload_b64).encode("utf-8")).decode("utf-8"))
        
        # Check expiration
        if payload_data.get("exp", 0) < time.time():
            return None
            
        return payload_data
    except Exception:
        return None


# Helper functions for password hashing
def hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()


# Dependency to get currently logged in user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    token = credentials.credentials
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的登录 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    username = payload.get("username")
    async with async_session() as db:
        stmt = select(User).where(User.username == username)
        res = await db.execute(stmt)
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user


# Dependency to get current admin user
async def get_current_admin(
    user: User = Depends(get_current_user)
) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只有管理员可访问此资源",
        )
    return user


@router.post("/register", response_model=ApiResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Check if username exists
    stmt = select(User).where(User.username == req.username)
    res = await db.execute(stmt)
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="用户名已被注册")

    # Generate salt and password hash
    salt = secrets.token_hex(16)
    password_hash = hash_password(req.password, salt)

    user = User(
        username=req.username,
        password_hash=password_hash,
        salt=salt,
        role=req.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return ApiResponse(data={"id": user.id, "username": user.username, "role": user.role})


@router.post("/login", response_model=ApiResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.username == req.username)
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # Verify password
    computed_hash = hash_password(req.password, user.salt)
    if computed_hash != user.password_hash:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # Generate new login JWT token
    jwt_exp = getattr(settings, "JWT_EXPIRATION", 1800)
    token = create_jwt(
        {"id": user.id, "username": user.username, "role": user.role},
        expires_in=jwt_exp
    )
    # JWT 鉴权无需写入数据库 users 表的 token 字段（该字段有 VARCHAR(128) 长度限制，写入 JWT 会抛出 DataTooLong 错误）
    # 故不设置 user.token，也不需要执行 commit

    return ApiResponse(data={
        "access_token": token,
        "token": token,  # 兼容现有前端 (api.js / LoginView.vue)
        "token_type": "bearer",
        "expires_in": jwt_exp,
        "username": user.username,
        "role": user.role
    })


@router.get("/me", response_model=ApiResponse)
async def get_me(user: User = Depends(get_current_user)):
    return ApiResponse(data={
        "id": user.id,
        "username": user.username,
        "role": user.role
    })
