"""
User API routes.

This module contains all user-related API endpoints including:
- User CRUD operations
- User management endpoints
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserBase
from app.models.user import User
from app.crud import user_crud
from app.services.auth_service import (
    get_current_user,
    restrict_to
)

router = APIRouter(prefix="/users", tags=["users"])


def check_user_access(user_id: int, current_user: User) -> None:
    """
    Helper function that checks if user can access specific user data.
    Users can access their own data, librarians and admins can access any data.
    """
    # User can access their own data
    if current_user.id == user_id:
        return

    # Librarians and admins can access any user's data
    from app.models.enums import RoleEnum
    if current_user.role in [RoleEnum.LIBRARIAN, RoleEnum.ADMIN]:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Not enough permissions to access this user's data"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
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
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of users to return"),
    search: Optional[str] = Query(None, description="Search users by name or email"),
    db: Session = Depends(get_db),
    current_user: User = Depends(restrict_to("librarian", "admin"))
):
    """
    Get all users with pagination and optional search.

    **Requires librarian or admin role.**

    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    - **search**: Optional search term to filter users by name or email
    """
    users = user_crud.get_multi_with_search(
        db=db, skip=skip, limit=limit, search=search
    )
    return users
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user to retrieve
    """
    # Check access permissions
    check_user_access(user_id, current_user)

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
    current_user: User = Depends(get_current_user)
):
    """
    Update a specific user by ID.

    **Requires authentication. Users can only update their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user to update
    - **name**: Updated user's full name
    - **email**: Updated user's email address
    - **role**: Updated user's role
    """
    # Check access permissions
    check_user_access(user_id, current_user)

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
    current_user: User = Depends(restrict_to("admin"))
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
@router.get("/{user_id}/reservations", response_model=List)
async def get_user_reservations(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reservations for a specific user.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user
    """
    # Check access permissions
    check_user_access(user_id, current_user)

    # Check if user exists
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # TODO: Implement get user reservations logic
    from app.crud.reservation import reservation as crud_reservation
    reservations = crud_reservation.get_by_user(db, user_id=user_id)
    return reservations
@router.get("/{user_id}/borrows", response_model=List)
async def get_user_borrows(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all borrows for a specific user.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user
    """
    # Check access permissions
    check_user_access(user_id, current_user)

    # Check if user exists
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # TODO: Implement get user borrows logic
    from app.crud.borrow import borrow as crud_borrow
    borrows = crud_borrow.get_by_user(db, user_id=user_id)
    return borrows
@router.get("/{user_id}/payments", response_model=List)
async def get_user_payments(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all payments for a specific user.

    **Requires authentication. Users can only access their own data unless they are librarian/admin.**

    - **user_id**: The ID of the user
    """
    # Check access permissions
    check_user_access(user_id, current_user)

    # Check if user exists
    db_user = user_crud.get(db=db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # TODO: Implement get user payments logic
    from app.crud.payment import payment as crud_payment
    payments = crud_payment.get_by_user(db, user_id=user_id)
    return payments