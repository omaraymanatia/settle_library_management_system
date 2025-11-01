from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models import PaymentTypeEnum, PaymentStatusEnum


class PaymentBase(BaseModel):
    amount: float
    payment_type: PaymentTypeEnum
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING


class PaymentCreate(PaymentBase):
    user_id: int


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    payment_date: datetime

    class Config:
        from_attributes = True
