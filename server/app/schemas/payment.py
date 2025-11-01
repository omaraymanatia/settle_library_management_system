from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from models.enums import PaymentTypeEnum, PaymentStatusEnum


class PaymentBase(BaseModel):
    amount: float
    payment_type: PaymentTypeEnum
    status: PaymentStatusEnum = PaymentStatusEnum.PENDING


class PaymentCreate(PaymentBase):
    user_id: int


class PaymentUpdate(BaseModel):
    amount: Optional[float] = None
    status: Optional[PaymentStatusEnum] = None


class PaymentResponse(PaymentBase):
    id: int
    user_id: int
    payment_date: datetime

    class Config:
        from_attributes = True
