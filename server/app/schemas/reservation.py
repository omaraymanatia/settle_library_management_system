from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import ReservationStatusEnum
from .book import BookResponse
from .payment import PaymentResponse


class ReservationBase(BaseModel):
    reservation_date: Optional[datetime] = None
    expiry_date: datetime
    status: ReservationStatusEnum = ReservationStatusEnum.RESERVED


class ReservationCreate(ReservationBase):
    book_id: int
    user_id: int
    payment_id: Optional[int]


class ReservationResponse(ReservationBase):
    id: int
    book_id: int
    user_id: int
    payment_id: Optional[int]
    book: Optional[BookResponse]
    payment: Optional[PaymentResponse]

    class Config:
        orm_mode = True
