"""
Authentication schemas for request/response models.
"""

from pydantic import BaseModel, EmailStr
from datetime import datetime
from models.enums import RoleEnum
from config import ACCESS_TOKEN_EXPIRE_MINUTES

# Token expiry time in seconds
ACCESS_TOKEN_EXPIRE_SECONDS = ACCESS_TOKEN_EXPIRE_MINUTES * 60


class RegisterRequest(BaseModel):
    """Register request schema."""
    name: str
    email: EmailStr
    password: str


class RegisterResponse(BaseModel):
    """Register response schema."""
    id: int
    name: str
    email: EmailStr
    role: RoleEnum
    created_at: datetime
    message: str = "User registered successfully"

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS  # seconds
    message: str = "Token generated successfully"


class UserInfo(BaseModel):
    """User information for auth responses."""
    id: int
    name: str
    email: EmailStr
    role: RoleEnum


class LoginResponse(BaseModel):
    """Login response schema with typed user info."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo
    message: str = "Login successful"


class LogoutResponse(BaseModel):
    """Logout response schema."""
    message: str = "Successfully logged out"


class VerifyTokenResponse(BaseModel):
    """Token verification response schema."""
    valid: bool = True
    user: UserInfo
    message: str = "Token is valid"