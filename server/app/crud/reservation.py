"""
CRUD operations for reservations.
"""

from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from datetime import datetime
from crud.base import CRUDBase
from models.reservation import Reservation
from models.enums import ReservationStatusEnum, PaymentStatusEnum
from schemas.reservation import ReservationCreate, ReservationBase


class CRUDReservation(CRUDBase[Reservation, ReservationCreate, ReservationBase]):
    def get_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Reservation]:
        """Get reservations by user ID."""
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .options(joinedload(self.model.book), joinedload(self.model.payment))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_book(
        self, db: Session, *, book_id: int, skip: int = 0, limit: int = 100
    ) -> List[Reservation]:
        """Get reservations by book ID."""
        return (
            db.query(self.model)
            .filter(self.model.book_id == book_id)
            .options(joinedload(self.model.user), joinedload(self.model.payment))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_active_reservation(
        self, db: Session, *, user_id: int, book_id: int
    ) -> Optional[Reservation]:
        """Get active reservation for a user and book."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.user_id == user_id,
                    self.model.book_id == book_id,
                    or_(
                        self.model.status == ReservationStatusEnum.PENDING,
                        self.model.status == ReservationStatusEnum.RESERVED
                    )
                )
            )
            .first()
        )

    def get_pending_reservations(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[Reservation]:
        """Get all pending reservations."""
        return (
            db.query(self.model)
            .filter(self.model.status == ReservationStatusEnum.PENDING)
            .options(joinedload(self.model.book), joinedload(self.model.user), joinedload(self.model.payment))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_expired_reservations(self, db: Session) -> List[Reservation]:
        """Get all expired reservations that haven't been marked as expired."""
        now = datetime.utcnow()
        return (
            db.query(self.model)
            .filter(
                and_(
                    self.model.expiry_date < now,
                    self.model.status != ReservationStatusEnum.EXPIRED,
                    self.model.status != ReservationStatusEnum.BORROWED
                )
            )
            .all()
        )

    def update_status(
        self, db: Session, *, reservation_id: int, status: ReservationStatusEnum
    ) -> Optional[Reservation]:
        """Update reservation status."""
        reservation = self.get(db, reservation_id)
        if reservation:
            reservation.status = status
            db.commit()
            db.refresh(reservation)
        return reservation

    def get_reservation_with_paid_deposit(
        self, db: Session, *, reservation_id: int
    ) -> Optional[Reservation]:
        """Get reservation with paid deposit."""
        return (
            db.query(self.model)
            .options(joinedload(self.model.payment))
            .filter(
                and_(
                    self.model.id == reservation_id,
                    self.model.payment_id.isnot(None)
                )
            )
            .first()
        )


# Create instance
reservation = CRUDReservation(Reservation)