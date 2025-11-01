"""
User API routes.

This module contains all user-related API endpoints including:
- User CRUD operations
- User management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.user import UserCreate, UserResponse, UserBase
from models.user import User
from crud import user_crud
from services.auth_service import (
    get_current_active_user,
    require_admin_role,
    require_librarian_role,
    check_user_permission
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the current authenticated user's profile.

    **Requires authentication.**

    Returns the profile of the currently logged-in user.
    """
    return current_user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user.

    - **name**: User's full name
    - **email**: User's email address (must be unique)
    - **role**: User's role (USER, LIBRARIAN, ADMIN)
    - **password**: User's password
    """
    try:
        db_user = user_crud.create(db=db, obj_in=user)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[UserResponse])
async def get_users(
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: Optional[str] = Query(None, description="Search users by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_librarian_role)
):
    """
    Get all users with pagination and optional search.

    **Requires librarian or admin role.**

    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    - **search**: Optional search term to filter users by name or email
    """
    users = user_crud.get_multi_with_search(
        db=db, limit=limit, search=search
    )
    return users
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific user by ID.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user to retrieve
    """
    # Check permissions
    if not check_user_permission(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user's data"
        )

    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a specific user by ID.

    **Requires authentication. Users can only update their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user to update
    - **name**: Updated user's full name
    - **email**: Updated user's email address
    - **role**: Updated user's role
    """
    # Check permissions
    if not check_user_permission(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this user's data"
        )

    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    try:
        updated_user = user_crud.update(db=db, db_obj=db_user, obj_in=user_update)
        return updated_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_role)
):
    """
    Delete a specific user by ID.

    **Requires admin role.**

    - **user_id**: The ID of the user to delete
    """
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user_crud.remove(db=db, id=user_id)
@router.get("/{user_id}/reservations")
async def get_user_reservations(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all reservations for a specific user.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user
    """
    # Check permissions
    if not check_user_permission(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user's data"
        )

    # Check if user exists
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # TODO: Implement get user reservations logic
    # For now, return empty list - this will be implemented when reservation CRUD is ready
    return []
@router.get("/{user_id}/borrows")
async def get_user_borrows(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all borrows for a specific user.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user
    """
    # Check permissions
    if not check_user_permission(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user's data"
        )

    # Check if user exists
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # TODO: Implement get user borrows logic
    # For now, return empty list - this will be implemented when borrow CRUD is ready
    return []
@router.get("/{user_id}/payments")
async def get_user_payments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all payments for a specific user.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user
    """
        # Check permissions
    if not check_user_permission(current_user, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this user's data"
        )

    # Check if user exists
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # TODO: Implement get user payments logic
    # For now, return empty list - this will be implemented when payment CRUD is ready
    return []