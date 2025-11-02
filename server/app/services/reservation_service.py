"""
Reservation service containing business logic for reservation operations.
"""

from typing import Optional, Tuple, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_, or_, select, func
from fastapi import HTTPException, status

from app.crud.reservation import reservation as crud_reservation
from app.crud.payment import payment as crud_payment
from app.crud.book import book_crud
from app.models.book import Book
from app.models.reservation import Reservation
from app.models.payment import Payment
from app.models.enums import ReservationStatusEnum, PaymentStatusEnum, PaymentTypeEnum
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.schemas.payment import PaymentCreate
from app.config import settings


class ReservationService:
    def __init__(self):
        self.reservation_expiry_hours = settings.RESERVATION_EXPIRY_HOURS
        self.deposit_percentage = settings.DEPOSIT_PERCENTAGE

    def create_reservation(
        self,
        db: Session,
        *,
        user_id: int,
        book_id: int,
        deposit_amount: Optional[float] = None
    ) -> Tuple[ReservationResponse, Optional[int]]:
        """
        Create a reservation with business logic:
        1. Check if book is available
        2. Check if user doesn't have active reservation for this book
        3. Create reservation in PENDING status
        4. Create deposit payment in PENDING status
        5. Return reservation and payment ID for frontend to process payment

        Returns: (reservation, payment_id)
        """

        # Start transaction
        try:
            # Check if book exists and has available quantity
            book = book_crud.get(db, book_id)
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )

            if book.available_quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Book is not available for reservation"
                )

            # Check if user already has an active reservation for this book
            existing_reservation = db.query(Reservation).filter(
                and_(
                    Reservation.user_id == user_id,
                    Reservation.book_id == book_id,
                    Reservation.status.in_([ReservationStatusEnum.PENDING, ReservationStatusEnum.RESERVED])
                )
            ).first()
            if existing_reservation:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You already have an active reservation for this book"
                )

            # Calculate deposit amount if not provided
            if deposit_amount is None:
                # Assuming we have a book_class with a value field, fallback to fixed amount
                deposit_amount = 10.0  # Default deposit amount
                if hasattr(book, 'book_class') and book.book_class:
                    # You can adjust this based on your book class pricing logic
                    deposit_amount = 10.0 * self.deposit_percentage

            # Create deposit payment in PENDING status
            payment_data = PaymentCreate(
                amount=deposit_amount,
                payment_type=PaymentTypeEnum.DEPOSIT,
                status=PaymentStatusEnum.PENDING,
                user_id=user_id
            )
            payment = crud_payment.create(db, obj_in=payment_data)

            # Create reservation in PENDING status with expiry time
            expiry_date = datetime.now(timezone.utc) + timedelta(hours=self.reservation_expiry_hours)
            reservation_data = ReservationCreate(
                book_id=book_id,
                user_id=user_id,
                payment_id=payment.id,
                expiry_date=expiry_date,
                status=ReservationStatusEnum.PENDING
            )

            reservation = crud_reservation.create(db, obj_in=reservation_data)

            # Convert to response schema
            reservation_response = ReservationResponse.model_validate(reservation)

            return reservation_response, payment.id

        except IntegrityError as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create reservation due to database constraint"
            )
        except Exception as e:
            db.rollback()
            raise e

    def confirm_reservation_payment(
        self,
        db: Session,
        *,
        reservation_id: int,
        payment_id: int
    ) -> ReservationResponse:
        """
        Confirm reservation payment and update book availability.
        This should be called when payment is successfully processed.

        Atomically:
        1. Mark payment as PAID
        2. Mark reservation as RESERVED
        3. Decrement book available_quantity
        """

        try:
            # Get reservation
            reservation = crud_reservation.get(db, reservation_id)
            if not reservation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found"
                )

            # Check if payment belongs to this reservation
            if reservation.payment_id != payment_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment does not belong to this reservation"
                )

            # Get payment
            payment = crud_payment.get(db, payment_id)
            if not payment or payment.status != PaymentStatusEnum.PENDING:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment not found or already processed"
                )

            # Check if reservation is still valid (not expired)
            if reservation.expiry_date < datetime.now(timezone.utc):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reservation has expired"
                )

            # Get book and check availability using database lock
            book = db.query(Book).filter(Book.id == reservation.book_id).with_for_update().first()
            if not book:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Book not found"
                )

            if book.available_quantity <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Book is no longer available"
                )

            # Atomically update payment, reservation, and book
            payment.status = PaymentStatusEnum.PAID
            reservation.status = ReservationStatusEnum.RESERVED
            book.available_quantity -= 1

            db.commit()
            db.refresh(reservation)

            return ReservationResponse.model_validate(reservation)

        except Exception as e:
            db.rollback()
            raise e

    def cancel_reservation(
        self,
        db: Session,
        *,
        reservation_id: int,
        user_id: int
    ) -> bool:
        """
        Cancel a reservation and handle refunds if applicable.
        """

        try:
            reservation = crud_reservation.get(db, reservation_id)
            if not reservation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reservation not found"
                )

            # Check ownership
            if reservation.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to cancel this reservation"
                )

            # Check if reservation can be cancelled
            if reservation.status in [ReservationStatusEnum.BORROWED, ReservationStatusEnum.EXPIRED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot cancel reservation in current status"
                )

            # If reservation was confirmed (RESERVED), restore book quantity
            if reservation.status == ReservationStatusEnum.RESERVED:
                book = db.query(Book).filter(Book.id == reservation.book_id).with_for_update().first()
                if book:
                    book.available_quantity += 1

            # Mark reservation as expired (cancelled)
            reservation.status = ReservationStatusEnum.EXPIRED

            # If payment exists and was paid, mark for refund processing
            if reservation.payment_id:
                payment = crud_payment.get(db, reservation.payment_id)
                if payment and payment.status == PaymentStatusEnum.PAID:
                    # In a real system, you'd initiate refund process here
                    # For now, we'll just mark it as failed (indicating refund needed)
                    payment.status = PaymentStatusEnum.FAILED

            db.commit()
            return True

        except Exception as e:
            db.rollback()
            raise e

    def expire_old_reservations(self, db: Session) -> int:
        """
        Expire old reservations and restore book quantities.
        This should be called periodically (e.g., via cron job).
        """
        # Get expired reservations
        expired_reservations = db.query(Reservation).filter(
            and_(
                Reservation.expiry_date < datetime.now(timezone.utc),
                Reservation.status.in_([ReservationStatusEnum.PENDING, ReservationStatusEnum.RESERVED])
            )
        ).all()

        count = 0

        for reservation in expired_reservations:
            try:
                # If reservation was confirmed, restore book quantity
                if reservation.status == ReservationStatusEnum.RESERVED:
                    book = db.query(Book).filter(Book.id == reservation.book_id).with_for_update().first()
                    if book:
                        book.available_quantity += 1

                # Mark as expired
                reservation.status = ReservationStatusEnum.EXPIRED
                count += 1

            except Exception as e:
                # Log error but continue with other reservations
                print(f"Error expiring reservation {reservation.id}: {str(e)}")
                continue

        if count > 0:
            db.commit()

        return count

    def get_user_reservations(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReservationResponse]:
        """Get all reservations for a user."""

        reservations = crud_reservation.get_by_user(
            db, user_id=user_id, skip=skip, limit=limit
        )

        return [ReservationResponse.model_validate(reservation) for reservation in reservations]

    def get_book_reservations(
        self,
        db: Session,
        *,
        book_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[ReservationResponse]:
        """Get all reservations for a book."""

        reservations = crud_reservation.get_by_book(
            db, book_id=book_id, skip=skip, limit=limit
        )

        return [ReservationResponse.model_validate(reservation) for reservation in reservations]


# Create instance
reservation_service = ReservationService()