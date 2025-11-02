"""
Borrow management API routes.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.book import Book
from app.models.reservation import Reservation
from app.models.payment import Payment
from app.models.enums import (
    BorrowStatusEnum,
    PaymentStatusEnum,
    PaymentTypeEnum,
    ReservationStatusEnum,
    RoleEnum
)
from app.schemas.borrow import (
    BorrowRequest,
    BorrowResponse,
    BorrowApprovalRequest,
    BorrowReturnRequest
)
from app.schemas.payment import PaymentCreate
from app.crud import borrow, book_crud as book, reservation, payment, user_crud as user
from app.services.auth_service import get_current_user, restrict_to
from app.services.borrow_service import borrow_service


router = APIRouter(prefix="/borrows", tags=["borrows"])


def calculate_borrow_fee(db: Session, book_id: int, reservation_id: Optional[int] = None) -> float:
    """Calculate the borrow fee for a book, considering any existing deposit."""
    book_obj = book.get(db, book_id)
    if not book_obj or not book_obj.book_class:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book or book class not found"
        )

    reservation_obj = None
    if reservation_id:
        reservation_obj = reservation.get(db, reservation_id)

    return borrow_service.calculate_borrow_fee(db, book_obj, reservation_obj)


def calculate_due_date(db: Session, book_id: int) -> datetime:
    """Calculate due date based on book class (default 14 days for now)."""
    # This could be enhanced to use book class specific borrow periods
    return datetime.utcnow() + timedelta(days=14)


def calculate_fine(db: Session, borrow_obj) -> float:
    """Calculate fine for late return."""
    return borrow_service.calculate_fine(borrow_obj)


@router.post("/request", response_model=BorrowResponse)
def create_borrow_request(
    borrow_request: BorrowRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new borrow request.

    The user must pay the borrow fee before the request can be approved.
    If the user has a reservation with paid deposit, it will be deducted from the borrow fee.
    """
    # Check if book exists and is available
    book_obj = book.get(db, borrow_request.book_id)
    if not book_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    if book_obj.available_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not available for borrowing"
        )

    # Check if user already has an active borrow for this book
    existing_borrow = borrow.get_active_borrow(
        db, user_id=current_user.id, book_id=borrow_request.book_id
    )
    if existing_borrow:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active borrow request for this book"
        )

    # Validate reservation if provided
    reservation_obj = None
    if borrow_request.reservation_id:
        reservation_obj = reservation.get(db, borrow_request.reservation_id)
        if not reservation_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )

        if reservation_obj.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This reservation does not belong to you"
            )

        if reservation_obj.book_id != borrow_request.book_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation is not for this book"
            )

        if reservation_obj.status != ReservationStatusEnum.RESERVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reservation is not in reserved status"
            )

    # Calculate due date
    due_date = borrow_request.due_date or calculate_due_date(db, borrow_request.book_id)

    # Create borrow record
    new_borrow = borrow.create_borrow_request(
        db,
        user_id=current_user.id,
        book_id=borrow_request.book_id,
        reservation_id=borrow_request.reservation_id,
        due_date=due_date
    )

    # Calculate and create pending payment for borrow fee
    borrow_fee = calculate_borrow_fee(db, borrow_request.book_id, borrow_request.reservation_id)

    if borrow_fee > 0:
        payment_data = PaymentCreate(
            amount=borrow_fee,
            payment_type=PaymentTypeEnum.BORROW_FEE,
            status=PaymentStatusEnum.PENDING,
            user_id=current_user.id
        )
        new_payment = payment.create(db, obj_in=payment_data)

        # Link payment to borrow
        new_borrow.payment_id = new_payment.id
        db.commit()
        db.refresh(new_borrow)

    return new_borrow


@router.get("/my-borrows", response_model=List[BorrowResponse])
def get_my_borrows(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's borrow history."""
    return borrow.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/pending-approval", response_model=List[BorrowResponse])
def get_pending_approval(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Get all borrow requests pending approval (admin only)."""
    return borrow.get_pending_approval(db, skip=skip, limit=limit)


@router.get("/pending-return", response_model=List[BorrowResponse])
def get_pending_return(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Get all borrows pending return (admin only)."""
    return borrow.get_pending_return(db, skip=skip, limit=limit)


@router.post("/{borrow_id}/approve", response_model=BorrowResponse)
def approve_or_reject_borrow(
    borrow_id: int,
    approval_request: BorrowApprovalRequest,
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Approve or reject a borrow request (admin only)."""
    borrow_obj = borrow.get(db, borrow_id)
    if not borrow_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow request not found"
        )

    if borrow_obj.status != BorrowStatusEnum.PENDING_APPROVAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow request is not pending approval"
        )

    if approval_request.approve:
        # Check if payment is completed
        if borrow_obj.payment and borrow_obj.payment.status != PaymentStatusEnum.PAID:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment must be completed before approval"
            )

        result = borrow.approve_borrow(db, borrow_id=borrow_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to approve borrow request"
            )
        return result
    else:
        result = borrow.reject_borrow(db, borrow_id=borrow_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to reject borrow request"
            )
        return result


@router.post("/{borrow_id}/request-return", response_model=BorrowResponse)
def request_return(
    borrow_id: int,
    return_request: BorrowReturnRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Request return of a borrowed book."""
    borrow_obj = borrow.get(db, borrow_id)
    if not borrow_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow record not found"
        )

    if borrow_obj.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This borrow record does not belong to you"
        )

    if borrow_obj.status != BorrowStatusEnum.BORROWED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not currently borrowed"
        )

    # Check if book is late and create fine payment if necessary
    if datetime.utcnow() > borrow_obj.due_date:
        fine_amount = calculate_fine(db, borrow_obj)
        if fine_amount > 0:
            fine_payment_data = PaymentCreate(
                amount=fine_amount,
                payment_type=PaymentTypeEnum.FINE,
                status=PaymentStatusEnum.PENDING,
                user_id=current_user.id
            )
            fine_payment = payment.create(db, obj_in=fine_payment_data)

            # Mark borrow as late
            borrow.mark_as_late(db, borrow_id=borrow_id)

    result = borrow.request_return(db, borrow_id=borrow_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to request return"
        )

    return result


@router.post("/{borrow_id}/complete-return", response_model=BorrowResponse)
def complete_return(
    borrow_id: int,
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Complete the return of a borrowed book (admin only)."""
    borrow_obj = borrow.get(db, borrow_id)
    if not borrow_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow record not found"
        )

    if borrow_obj.status != BorrowStatusEnum.RETURN_PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Borrow is not pending return"
        )

    result = borrow.complete_return(db, borrow_id=borrow_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to complete return"
        )

    return result


@router.get("/overdue", response_model=List[BorrowResponse])
def get_overdue_borrows(
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Get all overdue borrows (admin only)."""
    return borrow.get_overdue_borrows(db)


@router.get("/{borrow_id}", response_model=BorrowResponse)
def get_borrow(
    borrow_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific borrow record."""
    borrow_obj = borrow.get(db, borrow_id)
    if not borrow_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow record not found"
        )

    # Users can only see their own borrows, admins can see all
    if current_user.role != RoleEnum.ADMIN and borrow_obj.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return borrow_obj


@router.get("/", response_model=List[BorrowResponse])
def get_all_borrows(
    skip: int = 0,
    limit: int = 100,
    status_filter: BorrowStatusEnum = None,
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Get all borrow records with optional status filter (admin only)."""
    if status_filter:
        return borrow.get_by_status(db, status=status_filter, skip=skip, limit=limit)
    else:
        return borrow.get_multi(db, skip=skip, limit=limit)


@router.post("/process-overdue")
def process_overdue_borrows(
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Process all overdue borrows and create fine payments (admin only)."""
    processed = borrow_service.process_overdue_borrows(db)
    return {
        "message": f"Processed {len(processed)} overdue borrows",
        "processed": processed
    }


@router.get("/statistics")
def get_borrow_statistics(
    current_user: User = Depends(restrict_to("admin")),
    db: Session = Depends(get_db)
):
    """Get borrow statistics for dashboard (admin only)."""
    return borrow_service.get_borrow_statistics(db)