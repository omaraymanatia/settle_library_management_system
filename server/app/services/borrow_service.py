"""
Borrow management service.

This module provides business logic for borrow operations,
including overdue handling and fine calculations.
"""

from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from crud import borrow, payment
from models.enums import PaymentTypeEnum, PaymentStatusEnum, BorrowStatusEnum
from schemas.payment import PaymentCreate


class BorrowService:
    """Service class for borrow management operations."""

    @staticmethod
    def process_overdue_borrows(db: Session) -> List[dict]:
        """
        Process all overdue borrows and create fine payments.
        Returns a list of processed borrow information.
        """
        overdue_borrows = borrow.get_overdue_borrows(db)
        processed = []

        for borrow_obj in overdue_borrows:
            try:
                # Calculate fine amount
                days_late = (datetime.utcnow() - borrow_obj.due_date).days
                if days_late <= 0:
                    continue

                fine_amount = days_late * borrow_obj.book.book_class.fine_per_day

                # Check if fine payment already exists for this borrow
                existing_fine = (
                    db.query(payment.model)
                    .filter(
                        payment.model.user_id == borrow_obj.user_id,
                        payment.model.payment_type == PaymentTypeEnum.FINE,
                        payment.model.status == PaymentStatusEnum.PENDING
                    )
                    .join(borrow.model)
                    .filter(borrow.model.id == borrow_obj.id)
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
                    fine_payment = payment.create(db, obj_in=fine_payment_data)

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
                borrow.mark_as_late(db, borrow_id=borrow_obj.id)

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
            days_late = (datetime.utcnow() - borrow_obj.due_date).days

        if days_late <= 0:
            return 0.0

        return days_late * borrow_obj.book.book_class.fine_per_day

    @staticmethod
    def get_borrow_statistics(db: Session) -> dict:
        """Get borrow statistics for dashboard."""
        stats = {
            "total_borrows": len(borrow.get_multi(db, limit=10000)),
            "pending_approval": len(borrow.get_pending_approval(db, limit=10000)),
            "pending_return": len(borrow.get_pending_return(db, limit=10000)),
            "overdue": len(borrow.get_overdue_borrows(db)),
            "by_status": {}
        }

        # Get counts by status
        for status in BorrowStatusEnum:
            count = len(borrow.get_by_status(db, status=status, limit=10000))
            stats["by_status"][status.value] = count

        return stats


# Create service instance
borrow_service = BorrowService()