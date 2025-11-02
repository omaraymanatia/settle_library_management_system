from pydantic import BaseModel
from datetime import datetime
from models.enums import BookClassNameEnum


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
        from_attributes = True
