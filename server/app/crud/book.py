"""
Book CRUD operations.

This module contains CRUD operations specific to the Book model.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from crud.base import CRUDBase
from models.book import Book
from schemas.book import BookCreate, BookBase


class CRUDBook(CRUDBase[Book, BookCreate, BookBase]):
    """CRUD operations for Book model."""

    def get_by_isbn(self, db: Session, *, isbn: str) -> Optional[Book]:
        """Get book by ISBN."""
        return db.query(Book).filter(Book.isbn == isbn).first()

    def create(self, db: Session, *, obj_in: BookCreate) -> Book:
        """Create a new book with ISBN uniqueness check."""
        # Check if ISBN already exists
        if self.get_by_isbn(db, isbn=obj_in.isbn):
            raise ValueError("ISBN already exists")

        # Validate quantities
        if obj_in.available_quantity > obj_in.total_quantity:
            raise ValueError("Available quantity cannot be greater than total quantity")

        if obj_in.total_quantity < 0 or obj_in.available_quantity < 0:
            raise ValueError("Quantities cannot be negative")

        # Create book object
        create_data = obj_in.dict()
        db_obj = Book(**create_data)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Book, obj_in: BookBase) -> Book:
        """Update book with ISBN uniqueness check."""
        update_data = obj_in.dict(exclude_unset=True)

        # Check if ISBN is being changed and if it already exists
        if "isbn" in update_data and update_data["isbn"] != db_obj.isbn:
            if self.get_by_isbn(db, isbn=update_data["isbn"]):
                raise ValueError("ISBN already exists")

        # Validate quantities if they're being updated
        total_qty = update_data.get("total_quantity", db_obj.total_quantity)
        available_qty = update_data.get("available_quantity", db_obj.available_quantity)

        if available_qty > total_qty:
            raise ValueError("Available quantity cannot be greater than total quantity")

        if total_qty < 0 or available_qty < 0:
            raise ValueError("Quantities cannot be negative")

        # Update the object
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_with_search(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        book_class_id: Optional[int] = None,
        available_only: bool = False
    ) -> List[Book]:
        """
        Get multiple books with optional search and filters.

        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            search: Search term for title, author, or ISBN
            book_class_id: Filter by book class
            available_only: Only return books with available_quantity > 0
        """
        query = db.query(Book)

        # Apply search filter
        if search:
            search_filter = or_(
                Book.title.ilike(f"%{search}%"),
                Book.author.ilike(f"%{search}%"),
                Book.isbn.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)

        # Apply book class filter
        if book_class_id:
            query = query.filter(Book.book_class_id == book_class_id)

        # Apply availability filter
        if available_only:
            query = query.filter(Book.available_quantity > 0)

        return query.offset(skip).limit(limit).all()

    def get_available_books(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Book]:
        """Get books that are available for borrowing."""
        return db.query(Book).filter(Book.available_quantity > 0).offset(skip).limit(limit).all()

    def update_availability(self, db: Session, *, book_id: int, quantity_change: int) -> Book:
        """
        Update book availability (for borrowing/returning).

        Args:
            book_id: ID of the book
            quantity_change: Positive to increase availability (return), negative to decrease (borrow)
        """
        db_obj = self.get(db, id=book_id)
        if not db_obj:
            raise ValueError("Book not found")

        new_available = db_obj.available_quantity + quantity_change

        if new_available < 0:
            raise ValueError("Not enough books available")

        if new_available > db_obj.total_quantity:
            raise ValueError("Available quantity cannot exceed total quantity")

        db_obj.available_quantity = new_available
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instance
book_crud = CRUDBook(Book)