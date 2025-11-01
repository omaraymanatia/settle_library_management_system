from pydantic import BaseModel
from datetime import datetime
from models import BookClassNameEnum


class BookClassBase(BaseModel):
    name: BookClassNameEnum
    borrow_fee: float
    deposit_amount: float
    fine_per_day: float


class BookClassCreate(BookClassBase):
    pass


class BookClassResponse(BookClassBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
