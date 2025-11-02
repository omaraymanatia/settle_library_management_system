from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from models import BorrowStatusEnum
from .book import BookResponse
from .payment import PaymentResponse
from .user import UserResponse
from .reservation import ReservationResponse


class BorrowBase(BaseModel):
    borrow_date: Optional[datetime] = None
    due_date: datetime
    return_date: Optional[datetime] = None
    status: BorrowStatusEnum = BorrowStatusEnum.PENDING_APPROVAL
    book_id: int
    user_id: int
    reservation_id: Optional[int] = None
    payment_id: Optional[int] = None


class BorrowRequest(BaseModel):
    book_id: int
    reservation_id: Optional[int] = None
    due_date: Optional[datetime] = None  # If not provided, will be calculated based on book class


class BorrowCreate(BorrowBase):
    pass


class BorrowUpdate(BaseModel):
    status: Optional[BorrowStatusEnum] = None
    return_date: Optional[datetime] = None


class BorrowResponse(BorrowBase):
    id: int
    book: Optional[BookResponse] = None
    user: Optional[UserResponse] = None
    payment: Optional[PaymentResponse] = None
    reservation: Optional[ReservationResponse] = None

    class Config:
        from_attributes = True


class BorrowApprovalRequest(BaseModel):
    approve: bool = Field(..., description="True to approve, False to reject")


class BorrowReturnRequest(BaseModel):
    """Request schema for returning a borrowed book."""
    pass  # No additional fields needed - the borrow_id comes from the URL path
