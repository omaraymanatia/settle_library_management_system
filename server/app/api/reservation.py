"""
Reservation API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import get_current_user
from app.services.reservation_service import reservation_service
from app.schemas.reservation import ReservationResponse
from app.schemas.user import UserResponse
from app.models.enums import ReservationStatusEnum

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("/", response_model=dict)
async def create_reservation(
    book_id: int,
    deposit_amount: Optional[float] = None,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new reservation for a book.

    This creates a reservation in PENDING status and a deposit payment in PENDING status.
    The client should then process the payment using the returned payment_id.
    """

    reservation, payment_id = reservation_service.create_reservation(
        db, user_id=current_user.id, book_id=book_id, deposit_amount=deposit_amount
    )

    return {
        "reservation": reservation,
        "payment_id": payment_id,
        "message": "Reservation created. Please complete the deposit payment to confirm."
    }


@router.put("/{reservation_id}/confirm-payment", response_model=ReservationResponse)
async def confirm_reservation_payment(
    reservation_id: int,
    payment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Confirm reservation payment and activate the reservation.

    This should be called after the payment has been successfully processed.
    It will:
    1. Mark the payment as PAID
    2. Mark the reservation as RESERVED
    3. Decrement the book's available quantity
    """

    reservation = reservation_service.confirm_reservation_payment(
        db, reservation_id=reservation_id, payment_id=payment_id
    )

    return reservation


@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancel a reservation.

    If the reservation was confirmed, this will restore the book's available quantity.
    If a deposit was paid, it will be marked for refund.
    """

    success = reservation_service.cancel_reservation(
        db, reservation_id=reservation_id, user_id=current_user.id
    )

    if success:
        return {"message": "Reservation cancelled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to cancel reservation"
        )


@router.get("/my-reservations", response_model=List[ReservationResponse])
async def get_my_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all reservations for the current user."""

    reservations = reservation_service.get_user_reservations(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

    return reservations


@router.get("/book/{book_id}", response_model=List[ReservationResponse])
async def get_book_reservations(
    book_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all reservations for a specific book. (Admin or for own reservations)"""

    reservations = reservation_service.get_book_reservations(
        db, book_id=book_id, skip=skip, limit=limit
    )

    # Filter to only current user's reservations unless user is admin
    if current_user.role.value != "admin":
        reservations = [r for r in reservations if r.user_id == current_user.id]

    return reservations


@router.get("/{reservation_id}", response_model=ReservationResponse)
async def get_reservation(
    reservation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific reservation by ID."""

    from crud.reservation import reservation as crud_reservation

    reservation = crud_reservation.get(db, reservation_id)

    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found"
        )

    # Check if user owns the reservation or is admin
    if reservation.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this reservation"
        )

    return ReservationResponse.model_validate(reservation)


# Admin endpoints
@router.get("/", response_model=List[ReservationResponse])
async def get_all_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[ReservationStatusEnum] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all reservations (Admin only)."""

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    from crud.reservation import reservation as crud_reservation

    if status_filter:
        # You can implement status filtering in CRUD if needed
        reservations = crud_reservation.get_multi(db, skip=skip, limit=limit)
        reservations = [r for r in reservations if r.status == status_filter]
    else:
        reservations = crud_reservation.get_multi(db, skip=skip, limit=limit)

    return [ReservationResponse.model_validate(reservation) for reservation in reservations]


@router.post("/expire-old", response_model=dict)
async def expire_old_reservations(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Expire old reservations (Admin only)."""

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    count = reservation_service.expire_old_reservations(db)

    return {"message": f"Expired {count} reservations"}