"""
Base service class.

This module contains base service patterns and utilities.
"""

from typing import TypeVar, Generic, Type, List, Optional, Any
from sqlalchemy.orm import Session


ModelType = TypeVar("ModelType")


class BaseService(Generic[ModelType]):
    """
    Base service class with common CRUD operations.

    This provides a generic interface for basic database operations
    that can be inherited by specific service classes.
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records with pagination."""
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, obj_data: dict) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, id: int, obj_data: dict) -> Optional[ModelType]:
        """Update a record."""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return None

        for field, value in obj_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """Delete a record."""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return False

        db.delete(db_obj)
        db.commit()
        return True