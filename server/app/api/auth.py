"""
Authentication API routes.

This module contains authentication-related endpoints including:
- User registration
- User login
- Token management
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import UserCreate, UserResponse
from schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    TokenResponse,
    UserInfo,
    LogoutResponse,
    VerifyTokenResponse
)
from models.enums import RoleEnum
from crud import user_crud
from services.auth_service import (
    create_access_token,
    get_current_active_user,
    security,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    authenticate_user
)
from models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **password**: User's password (will be hashed)

    All new users are registered with USER role by default.
    """
    try:
        user_create = UserCreate(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password,
            role=RoleEnum.USER
        )

        db_user = user_crud.create(db=db, obj_in=user_create)

        # Return the response with the created user data
        return RegisterResponse(
            id=db_user.id,
            name=db_user.name,
            email=db_user.email,
            role=db_user.role,
            created_at=db_user.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Login user and return access token.

    - **email**: User's email address
    - **password**: User's password

    Returns:
    - **access_token**: JWT token for authentication
    - **token_type**: Token type (bearer)
    - **expires_in**: Token expiration time in seconds
    - **user**: User information
    """
    # Authenticate user
    user = authenticate_user(
        db=db, email=login_data.email, password=login_data.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Create typed user info
    user_info = UserInfo(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Convert to seconds
        user=user_info
    )
@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user.

    **Requires valid authentication token.**

    Note: With JWT tokens, logout is typically handled client-side
    by removing the token. This endpoint confirms the logout action.
    """
    return LogoutResponse(message="Successfully logged out")
@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Refresh access token.

    **Requires valid authentication token.**

    Returns:
    - **access_token**: New JWT token
    - **token_type**: Token type (bearer)
    - **expires_in**: Token expiration time in seconds
    """
    # TODO: Implement token refresh logic
    # - Generate new access token for current user
    # - Return new token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
    }


@router.get("/verify", response_model=VerifyTokenResponse)
async def verify_token_endpoint(
    current_user: User = Depends(get_current_active_user)
):
    """
    Verify if the current token is valid.

    **Requires valid authentication token.**

    Returns user information if token is valid.
    """
    user_info = UserInfo(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role
    )

    return VerifyTokenResponse(
        valid=True,
        user=user_info
    )
