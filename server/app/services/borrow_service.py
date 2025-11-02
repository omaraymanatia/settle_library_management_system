"""
Borrow management service.

This module provides business logic for borrow operations,
including overdue handling and fine calculations.
"""

from typing import Optional, List, Tuple
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, select, func
from fastapi import HTTPException, status

from app.crud.borrow import borrow as borrow_crud
from app.crud.payment import payment as crud_payment
from app.crud.reservation import reservation as crud_reservation
from app.crud.book import book_crud
from app.models.borrow import Borrow
from app.models.payment import Payment
from app.models.enums import PaymentTypeEnum, PaymentStatusEnum, BorrowStatusEnum
from app.schemas.payment import PaymentCreate


class BorrowService:
    """Service class for borrow management operations."""

    @staticmethod
    def process_overdue_borrows(db: Session) -> List[dict]:
        """
        Process all overdue borrows and create fine payments.
        Returns a list of processed borrow information.
        """
        overdue_borrows = borrow_crud.get_overdue_borrows(db)
        processed = []

        for borrow_obj in overdue_borrows:
            try:
                # Calculate fine amount using the dedicated method
                fine_amount = BorrowService.calculate_fine(borrow_obj)
                if fine_amount <= 0:
                    continue

                # Calculate days late for reporting
                days_late = (datetime.now(timezone.utc) - borrow_obj.due_date).days

                # Check if fine payment already exists for this borrow
                existing_fine = (
                    db.query(Payment)
                    .filter(
                        Payment.user_id == borrow_obj.user_id,
                        Payment.payment_type == PaymentTypeEnum.FINE,
                        Payment.status == PaymentStatusEnum.PENDING
                    )
                    .first()
                )

                if not existing_fine:
                    # Create fine payment
                    fine_payment_data = PaymentCreate(
                        amount=fine_amount,
                        payment_type=PaymentTypeEnum.FINE,
                        status=PaymentStatusEnum.PENDING,
                        user_id=borrow_obj.user_id
                    )
                    fine_payment = crud_payment.create(db, obj_in=fine_payment_data)

                    processed.append({
                        "borrow_id": borrow_obj.id,
                        "user_id": borrow_obj.user_id,
                        "book_id": borrow_obj.book_id,
                        "days_late": days_late,
                        "fine_amount": fine_amount,
                        "fine_payment_id": fine_payment.id,
                        "action": "fine_created"
                    })

                # Mark borrow as late
                borrow_crud.mark_as_late(db, borrow_id=borrow_obj.id)

            except Exception as e:
                processed.append({
                    "borrow_id": borrow_obj.id,
                    "error": str(e),
                    "action": "error"
                })

        return processed

    @staticmethod
    def calculate_borrow_fee(
        db: Session,
        book_obj,
        reservation_obj=None
    ) -> float:
        """
        Calculate the borrow fee for a book, considering any existing deposit.
        """
        if not book_obj or not book_obj.book_class:
            return 0.0

        borrow_fee = book_obj.book_class.borrow_fee

        # If user has a reservation with paid deposit, subtract it from borrow fee
        if (reservation_obj and
            reservation_obj.payment and
            reservation_obj.payment.status == PaymentStatusEnum.PAID and
            reservation_obj.payment.payment_type == PaymentTypeEnum.DEPOSIT):
            borrow_fee -= reservation_obj.payment.amount

        return max(0, borrow_fee)  # Ensure fee is not negative

    @staticmethod
    def calculate_fine(borrow_obj) -> float:
        """Calculate fine for late return."""
        if not borrow_obj.book or not borrow_obj.book.book_class:
            return 0.0

        if borrow_obj.return_date:
            days_late = (borrow_obj.return_date - borrow_obj.due_date).days
        else:
            days_late = (datetime.now(timezone.utc) - borrow_obj.due_date).days

        if days_late <= 0:
            return 0.0

        return days_late * borrow_obj.book.book_class.fine_per_day

    @staticmethod
    def get_borrow_statistics(db: Session) -> dict:
        """Get borrow statistics for dashboard."""
        stats = {
            "total_borrows": db.query(func.count(Borrow.id)).scalar(),
            "pending_approval": db.query(func.count(Borrow.id)).filter(
                Borrow.status == BorrowStatusEnum.PENDING_APPROVAL
            ).scalar(),
            "pending_return": db.query(func.count(Borrow.id)).filter(
                Borrow.status == BorrowStatusEnum.RETURN_PENDING
            ).scalar(),
            "overdue": db.query(func.count(Borrow.id)).filter(
                Borrow.due_date < datetime.now(timezone.utc),
                Borrow.status == BorrowStatusEnum.BORROWED
            ).scalar(),
            "by_status": {}
        }

        # Get counts by status
        for status in BorrowStatusEnum:
            count = db.query(func.count(Borrow.id)).filter(
                Borrow.status == status
            ).scalar()
            stats["by_status"][status.value] = count

        return stats


# Create service instance
borrow_service = BorrowService()