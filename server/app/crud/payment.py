"""
CRUD operations for payments.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.crud.base import CRUDBase
from app.models.payment import Payment
from app.models.enums import PaymentTypeEnum, PaymentStatusEnum
from app.schemas.payment import PaymentCreate, PaymentBase


class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentBase]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get payments by user ID."""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_type(
        self,
        db: Session,
        *,
        payment_type: PaymentTypeEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """Get payments by type."""
        return (
            db.query(self.model)
            .filter(self.model.payment_type == payment_type)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: PaymentStatusEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Payment]:
        """Get payments by status."""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_deposit_for_book(
        self, db: Session, *, user_id: int, payment_type: PaymentTypeEnum = PaymentTypeEnum.DEPOSIT
    ) -> Optional[Payment]:
        """Get user's deposit payment."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.payment_type == payment_type,
                    self.model.status == PaymentStatusEnum.PAID
                )
            )
            .first()
        )

    def update_status(
        self, db: Session, *, payment_id: int, status: PaymentStatusEnum
    ) -> Optional[Payment]:
        """Update payment status."""
        payment = self.get(db, payment_id)
        if payment:
            payment.status = status
            db.commit()
            db.refresh(payment)
        return payment

    def get_pending_payments(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Payment]:
        """Get all pending payments."""
        return (
            db.query(self.model)
            .filter(self.model.status == PaymentStatusEnum.PENDING)
            .offset(skip)
            .limit(limit)
            .all()
        )


# Create instance
payment = CRUDPayment(Payment)