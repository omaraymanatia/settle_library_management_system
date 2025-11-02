from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.enums import ReservationStatusEnum
from .book import BookResponse
from .payment import PaymentResponse
from .user import UserResponse


class ReservationBase(BaseModel):
    reservation_date: Optional[datetime] = None
    expiry_date: datetime
    status: ReservationStatusEnum = ReservationStatusEnum.PENDING
    book_id: int
    user_id: int
    payment_id: Optional[int] = None


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    expiry_date: Optional[datetime] = None
    status: Optional[ReservationStatusEnum] = None
    payment_id: Optional[int] = None


class ReservationResponse(ReservationBase):
    id: int
    book: Optional[BookResponse] = None
    user: Optional[UserResponse] = None
    payment: Optional[PaymentResponse] = None

    class Config:
        from_attributes = True
