"""
User service.

This module contains business logic for user operations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.user import User
from schemas.user import UserCreate, UserBase, UserUpdate
from services.auth_service import get_password_hash


class UserService:
    """Service class for user operations."""

    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            user: User creation data

        Returns:
            Created user

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("Email already registered")

        # Hash password
        hashed_password = get_password_hash(user.password)

        # Create user
        db_user = User(
            name=user.name,
            email=user.email,
            role=user.role,
            password=hashed_password
        )

        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: User email

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[User]:
        """
        Get users with pagination and optional search.

        Args:
            db: Database session
            skip: Number of users to skip
            limit: Maximum number of users to return
            search: Search term for name or email

        Returns:
            List of users
        """
        query = db.query(User)

        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update user.

        Args:
            db: Database session
            user_id: User ID to update
            user_update: Updated user data

        Returns:
            Updated user if found, None otherwise

        Raises:
            ValueError: If email already exists for another user
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        # Check if email is being changed and if it already exists
        if user_update.email != db_user.email:
            existing_user = db.query(User).filter(
                User.email == user_update.email,
                User.id != user_id
            ).first()
            if existing_user:
                raise ValueError("Email already registered")

        # Update fields
        for field, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, field, value)

        db.commit()
        db.refresh(db_user)

        return db_user

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        Delete user.

        Args:
            db: Database session
            user_id: User ID to delete

        Returns:
            True if user was deleted, False if not found
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()

        return True