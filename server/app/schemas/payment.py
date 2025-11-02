from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from models.enums import PaymentTypeEnum, PaymentStatusEnum


class PaymentBase(BaseModel):
    amount: float
    payment_type: PaymentTypeEnum
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING
    user_id: int


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    payment_type: Optional[PaymentTypeEnum] = None
    status: Optional[PaymentStatusEnum] = None


class PaymentResponse(PaymentBase):
    id: int
    payment_date: datetime
    # Note: user, reservations, and borrows relationships available but not included
    # to avoid circular imports and keep response clean

    class Config:
        from_attributes = True
