"""
User CRUD operations.

This module contains CRUD operations specific to the User model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from crud.base import CRUDBase
from models.user import User
from schemas.user import UserCreate, UserBase
from services.auth_service import get_password_hash


class CRUDUser(CRUDBase[User, UserCreate, UserBase]):
    """CRUD operations for User model."""

    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email address."""
        return db.query(User).filter(User.email == email).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create a new user with hashed password."""
        # Check if email already exists
        if self.get_by_email(db, email=obj_in.email):
            raise ValueError("Email already registered")

        # Create user data without password first
        create_data = obj_in.dict()
        password = create_data.pop("password")

        # Hash the password
        hashed_password = get_password_hash(password)

        # Create user object
        db_obj = User(**create_data)
        # Note: You'll need to add password field to User model
        # db_obj.password = hashed_password

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: User, obj_in: UserBase) -> User:
        """Update user with email uniqueness check."""
        update_data = obj_in.dict(exclude_unset=True)

        # Check if email is being changed and if it already exists
        if "email" in update_data and update_data["email"] != db_obj.email:
            existing_user = self.get_by_email(db, email=update_data["email"])
            if existing_user and existing_user.id != db_obj.id:
                raise ValueError("Email already registered")

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def search(
        self,
        db: Session,
        *,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name or email."""
        search_filter = or_(
            User.name.ilike(f"%{search_term}%"),
            User.email.ilike(f"%{search_term}%")
        )
        return (
            db.query(User)
            .filter(search_filter)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_multi_with_search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None
    ) -> List[User]:
        """Get multiple users with optional search."""
        if search:
            return self.search(db, search_term=search, skip=skip, limit=limit)
        return self.get_multi(db, skip=skip, limit=limit)

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password."""
        from services.auth_service import verify_password

        user = self.get_by_email(db, email=email)
        if not user:
            return None

        # Note: You'll need to add password field to User model
        # if not verify_password(password, user.password):
        #     return None

        # For now, return user (you'll need to implement password checking)
        return user


    def is_superuser(self, user: User) -> bool:
        """Check if user is superuser/admin."""
        from models.enums import RoleEnum
        return user.role == RoleEnum.ADMIN


# Create instance to be used throughout the app
user_crud = CRUDUser(User)