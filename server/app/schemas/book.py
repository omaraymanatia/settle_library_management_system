from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .book_class import BookClassResponse


class BookBase(BaseModel):
    isbn: str
    title: str
    author: str
    shelf_location: Optional[str]
    total_quantity: int
    available_quantity: int


class BookCreate(BookBase):
    book_class_id: Optional[int]


class BookResponse(BookBase):
    id: int
    created_at: datetime
    book_class: Optional[BookClassResponse]

    class Config:
        from_attributes = True
