from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import BorrowStatusEnum
from .book import BookResponse
from .payment import PaymentResponse


class BorrowBase(BaseModel):
    borrow_date: Optional[datetime] = None
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatusEnum = BorrowStatusEnum.PENDING_APPROVAL


class BorrowCreate(BorrowBase):
    book_id: int
    user_id: int
    reservation_id: Optional[int]
    payment_id: Optional[int]


class BorrowResponse(BorrowBase):
    id: int
    book_id: int
    user_id: int
    reservation_id: Optional[int]
    payment_id: Optional[int]
    book: Optional[BookResponse]
    payment: Optional[PaymentResponse]

    class Config:
        from_attributes = True
