"""
Book API routes.

This module contains all book-related API endpoints including:
- Book CRUD operations
- Book search and filtering
- Book availability management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from db.session import get_db
from schemas.book import BookCreate, BookResponse, BookBase
from models.book import Book
from models.user import User
from crud import book_crud
from services.auth_service import (
    protect,
    restrict_to
)

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(restrict_to("librarian", "admin"))
):
    """
    Create a new book.

    **Requires librarian or admin role.**

    - **isbn**: Book's ISBN (must be unique)
    - **title**: Book's title
    - **author**: Book's author
    - **shelf_location**: Physical location of the book (optional)
    - **total_quantity**: Total number of copies
    - **available_quantity**: Number of copies available for borrowing
    - **book_class_id**: ID of the book class (optional)
    """
    try:
        db_book = book_crud.create(db=db, obj_in=book)
        return db_book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of books to return"),
    search: Optional[str] = Query(None, description="Search books by title, author, or ISBN"),
    book_class_id: Optional[int] = Query(None, description="Filter by book class ID"),
    available_only: bool = Query(False, description="Show only available books"),
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    """
    Get all books with pagination and optional filters.

    **Requires authentication.**

    - **skip**: Number of books to skip (for pagination)
    - **limit**: Maximum number of books to return
    - **search**: Optional search term to filter books by title, author, or ISBN
    - **book_class_id**: Optional filter by book class
    - **available_only**: Only return books with available copies
    """
    books = book_crud.get_multi_with_search(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        book_class_id=book_class_id,
        available_only=available_only
    )
    return books


@router.get("/available", response_model=List[BookResponse])
async def get_available_books(
    skip: int = Query(0, ge=0, description="Number of books to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of books to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    """
    Get all books that are currently available for borrowing.

    **Requires authentication.**

    - **skip**: Number of books to skip (for pagination)
    - **limit**: Maximum number of books to return
    """
    books = book_crud.get_available_books(db=db, skip=skip, limit=limit)
    return books


@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    """
    Get a specific book by ID.

    **Requires authentication.**

    - **book_id**: The ID of the book to retrieve
    """
    db_book = book_crud.get(db=db, id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return db_book


@router.get("/isbn/{isbn}", response_model=BookResponse)
async def get_book_by_isbn(
    isbn: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(protect)
):
    """
    Get a specific book by ISBN.

    **Requires authentication.**

    - **isbn**: The ISBN of the book to retrieve
    """
    db_book = book_crud.get_by_isbn(db=db, isbn=isbn)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return db_book


@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: int,
    book_update: BookBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(restrict_to("librarian", "admin"))
):
    """
    Update a specific book by ID.

    **Requires librarian or admin role.**

    - **book_id**: The ID of the book to update
    - **isbn**: Updated book's ISBN
    - **title**: Updated book's title
    - **author**: Updated book's author
    - **shelf_location**: Updated physical location
    - **total_quantity**: Updated total number of copies
    - **available_quantity**: Updated number of available copies
    """
    db_book = book_crud.get(db=db, id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    try:
        updated_book = book_crud.update(db=db, db_obj=db_book, obj_in=book_update)
        return updated_book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(restrict_to("admin"))
):
    """
    Delete a specific book by ID.

    **Requires admin role.**

    - **book_id**: The ID of the book to delete
    """
    db_book = book_crud.get(db=db, id=book_id)
    if not db_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Check if book has active borrows or reservations
    if db_book.borrows or db_book.reservations:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete book with active borrows or reservations"
        )

    book_crud.remove(db=db, id=book_id)


@router.patch("/{book_id}/availability", response_model=BookResponse)
async def update_book_availability(
    book_id: int,
    quantity_change: int = Query(..., description="Change in available quantity (positive for returns, negative for borrows)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(restrict_to("librarian", "admin"))
):
    """
    Update book availability quantity.

    **Requires librarian or admin role.**

    This endpoint is typically used by the borrowing/returning system
    to update book availability when books are borrowed or returned.

    - **book_id**: The ID of the book
    - **quantity_change**: Positive number to increase availability (return), negative to decrease (borrow)
    """
    try:
        updated_book = book_crud.update_availability(
            db=db, book_id=book_id, quantity_change=quantity_change
        )
        return updated_book
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
