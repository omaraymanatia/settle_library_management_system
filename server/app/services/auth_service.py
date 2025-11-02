"""
Authentication service.

This module provides JWT token handling and authentication dependencies
for protecting API routes.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User
from models.enums import RoleEnum
from config import SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# HTTP Bearer scheme for token authentication
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.

    This dependency can be used to protect routes and get the current user.
    """
    token = credentials.credentials

    try:
        payload = verify_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user_id = int(user_id_str)
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current authenticated and active user.

    This can be extended to check if the user account is active/enabled.
    """
    # You can add additional checks here, like:
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")

    return current_user


def restrict_to(*roles):
    """
    Restrict access to specific roles - equivalent to your Node.js restrictTo function.

    Usage:
        @router.get("/admin-only")
        async def admin_endpoint(user: User = Depends(restrict_to("admin"))):
            pass

        @router.get("/librarian-or-admin")
        async def librarian_endpoint(user: User = Depends(restrict_to("librarian", "admin"))):
            pass
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # Convert string roles to RoleEnum for comparison
        role_mapping = {
            "user": RoleEnum.USER,
            "librarian": RoleEnum.LIBRARIAN,
            "admin": RoleEnum.ADMIN
        }

        allowed_roles = [role_mapping.get(role.lower()) for role in roles]
        allowed_roles = [role for role in allowed_roles if role is not None]

        if not allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Invalid roles specified: {roles}"
            )

        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )

        return current_user

    return role_checker