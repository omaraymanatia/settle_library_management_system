from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.enums import ReservationStatusEnum
from .book import BookResponse
from .payment import PaymentResponse


class ReservationBase(BaseModel):
    reservation_date: Optional[datetime] = None
    expiry_date: datetime
    status: ReservationStatusEnum = ReservationStatusEnum.PENDING


class ReservationCreate(ReservationBase):
    book_id: int
    user_id: int
    payment_id: Optional[int] = None


class ReservationUpdate(BaseModel):
    expiry_date: Optional[datetime] = None
    status: Optional[ReservationStatusEnum] = None
    payment_id: Optional[int] = None


class ReservationResponse(ReservationBase):
    id: int
    book_id: int
    user_id: int
    payment_id: Optional[int]
    book: Optional[BookResponse] = None
    payment: Optional[PaymentResponse] = None

    class Config:
        from_attributes = True
