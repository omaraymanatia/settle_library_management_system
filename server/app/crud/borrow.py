"""
CRUD operations for borrows.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
from crud.base import CRUDBase
from models.borrow import Borrow
from models.book import Book
from models.payment import Payment
from models.reservation import Reservation
from models.enums import (
    BorrowStatusEnum,
    PaymentStatusEnum,
    PaymentTypeEnum,
    ReservationStatusEnum
)
from schemas.borrow import BorrowCreate, BorrowBase


class CRUDBorrow(CRUDBase[Borrow, BorrowCreate, BorrowBase]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Borrow]:
        """Get borrows by user ID."""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .options(
                joinedload(self.model.book).joinedload(Book.book_class),
                joinedload(self.model.payment),
                joinedload(self.model.reservation)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_book(
        self, db: Session, *, book_id: int, skip: int = 0, limit: int = 100
    ) -> List[Borrow]:
        """Get borrows by book ID."""
        return (
            db.query(self.model)
            .filter(self.model.book_id == book_id)
            .options(
                joinedload(self.model.user),
                joinedload(self.model.payment),
                joinedload(self.model.reservation)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self,
        db: Session,
        *,
        status: BorrowStatusEnum,
        skip: int = 0,
        limit: int = 100
    ) -> List[Borrow]:
        """Get borrows by status."""
        return (
            db.query(self.model)
            .filter(self.model.status == status)
            .options(
                joinedload(self.model.book).joinedload(Book.book_class),
                joinedload(self.model.user),
                joinedload(self.model.payment)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending_approval(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Borrow]:
        """Get all borrows pending approval."""
        return (
            db.query(self.model)
            .filter(self.model.status == BorrowStatusEnum.PENDING_APPROVAL)
            .options(
                joinedload(self.model.book).joinedload(Book.book_class),
                joinedload(self.model.user),
                joinedload(self.model.payment)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_pending_return(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Borrow]:
        """Get all borrows pending return."""
        return (
            db.query(self.model)
            .filter(self.model.status == BorrowStatusEnum.RETURN_PENDING)
            .options(
                joinedload(self.model.book).joinedload(Book.book_class),
                joinedload(self.model.user),
                joinedload(self.model.payment)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_borrow(
        self, db: Session, *, user_id: int, book_id: int
    ) -> Optional[Borrow]:
        """Get active borrow for a user and book."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.book_id == book_id,
                    or_(
                        self.model.status == BorrowStatusEnum.PENDING_APPROVAL,
                        self.model.status == BorrowStatusEnum.BORROWED,
                        self.model.status == BorrowStatusEnum.RETURN_PENDING
                    )
                )
            )
            .first()
        )

    def get_overdue_borrows(self, db: Session) -> List[Borrow]:
        """Get all overdue borrows that haven't been marked as late."""
        now = datetime.utcnow()
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.due_date < now,
                    self.model.status == BorrowStatusEnum.BORROWED,
                    self.model.return_date.is_(None)
                )
            )
            .options(
                joinedload(self.model.book).joinedload(Book.book_class),
                joinedload(self.model.user)
            )
            .all()
        )

    def get_with_payment(
        self, db: Session, *, borrow_id: int
    ) -> Optional[Borrow]:
        """Get borrow with payment information."""
        return (
            db.query(self.model)
            .options(
                joinedload(self.model.payment),
                joinedload(self.model.book).joinedload(Book.book_class)
            )
            .filter(self.model.id == borrow_id)
            .first()
        )

    def update_status(
        self, db: Session, *, borrow_id: int, status: BorrowStatusEnum
    ) -> Optional[Borrow]:
        """Update borrow status."""
        borrow = self.get(db, borrow_id)
        if borrow:
            borrow.status = status
            if status == BorrowStatusEnum.RETURNED:
                borrow.return_date = datetime.utcnow()
            db.commit()
            db.refresh(borrow)
        return borrow

    def create_borrow_request(
        self,
        db: Session,
        *,
        user_id: int,
        book_id: int,
        reservation_id: Optional[int] = None,
        due_date: datetime
    ) -> Borrow:
        """Create a new borrow request."""
        borrow_data = {
            "user_id": user_id,
            "book_id": book_id,
            "reservation_id": reservation_id,
            "due_date": due_date,
            "status": BorrowStatusEnum.PENDING_APPROVAL
        }
        db_borrow = self.model(**borrow_data)
        db.add(db_borrow)
        db.commit()
        db.refresh(db_borrow)
        return db_borrow

    def approve_borrow(
        self, db: Session, *, borrow_id: int
    ) -> Optional[Borrow]:
        """Approve a borrow request."""
        borrow = self.get(db, borrow_id)
        if borrow and borrow.status == BorrowStatusEnum.PENDING_APPROVAL:
            # Check if payment is completed
            if borrow.payment and borrow.payment.status == PaymentStatusEnum.PAID:
                borrow.status = BorrowStatusEnum.BORROWED
                borrow.borrow_date = datetime.utcnow()

                # Update book availability
                book = db.query(Book).filter(Book.id == borrow.book_id).first()
                if book and book.available_quantity > 0:
                    book.available_quantity -= 1

                # Update reservation status if exists
                if borrow.reservation:
                    borrow.reservation.status = ReservationStatusEnum.BORROWED

                db.commit()
                db.refresh(borrow)
                return borrow
        return None

    def reject_borrow(
        self, db: Session, *, borrow_id: int
    ) -> Optional[Borrow]:
        """Reject a borrow request."""
        borrow = self.get(db, borrow_id)
        if borrow and borrow.status == BorrowStatusEnum.PENDING_APPROVAL:
            borrow.status = BorrowStatusEnum.REJECTED
            db.commit()
            db.refresh(borrow)
            return borrow
        return None

    def request_return(
        self, db: Session, *, borrow_id: int
    ) -> Optional[Borrow]:
        """Request return of a borrowed book."""
        borrow = self.get(db, borrow_id)
        if borrow and borrow.status == BorrowStatusEnum.BORROWED:
            borrow.status = BorrowStatusEnum.RETURN_PENDING
            db.commit()
            db.refresh(borrow)
            return borrow
        return None

    def complete_return(
        self, db: Session, *, borrow_id: int
    ) -> Optional[Borrow]:
        """Complete the return of a borrowed book."""
        borrow = self.get(db, borrow_id)
        if borrow and borrow.status == BorrowStatusEnum.RETURN_PENDING:
            borrow.status = BorrowStatusEnum.RETURNED
            borrow.return_date = datetime.utcnow()

            # Update book availability
            book = db.query(Book).filter(Book.id == borrow.book_id).first()
            if book:
                book.available_quantity += 1

            db.commit()
            db.refresh(borrow)
            return borrow
        return None

    def mark_as_late(
        self, db: Session, *, borrow_id: int
    ) -> Optional[Borrow]:
        """Mark a borrow as late."""
        borrow = self.get(db, borrow_id)
        if borrow:
            borrow.status = BorrowStatusEnum.LATE
            db.commit()
            db.refresh(borrow)
            return borrow
        return None


# Create instance
borrow = CRUDBorrow(Borrow)