"""
Payment API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import get_current_user
from app.crud.payment import payment as crud_payment
from app.schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.schemas.user import UserResponse
from app.models.enums import PaymentTypeEnum, PaymentStatusEnum

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new payment."""

    # Ensure user can only create payments for themselves (unless admin)
    if payment_data.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create payment for another user"
        )

    payment = crud_payment.create(db, obj_in=payment_data)
    return PaymentResponse.model_validate(payment)


@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    payment_type: Optional[PaymentTypeEnum] = Query(None),
    status_filter: Optional[PaymentStatusEnum] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all payments for the current user."""

    payments = crud_payment.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

    # Apply filters if provided
    if payment_type:
        payments = [p for p in payments if p.payment_type == payment_type]
    if status_filter:
        payments = [p for p in payments if p.status == status_filter]

    return [PaymentResponse.model_validate(payment) for payment in payments]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific payment by ID."""

    payment = crud_payment.get(db, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Check if user owns the payment or is admin
    if payment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )

    return PaymentResponse.model_validate(payment)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a payment (typically to mark as paid/failed)."""

    payment = crud_payment.get(db, payment_id)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    # Only admin or payment owner can update (for marking as paid by external processor)
    if payment.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this payment"
        )

    # Prevent changing to PAID status unless admin (external payment processor should do this)
    if payment_update.status == PaymentStatusEnum.PAID and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only payment processor can mark payment as paid"
        )

    updated_payment = crud_payment.update(db, db_obj=payment, obj_in=payment_update)
    return PaymentResponse.model_validate(updated_payment)


# Admin endpoints
@router.get("/", response_model=List[PaymentResponse])
async def get_all_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    payment_type: Optional[PaymentTypeEnum] = Query(None),
    status_filter: Optional[PaymentStatusEnum] = Query(None),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all payments (Admin only)."""

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    if payment_type:
        payments = crud_payment.get_by_type(db, payment_type=payment_type, skip=skip, limit=limit)
    elif status_filter:
        payments = crud_payment.get_by_status(db, status=status_filter, skip=skip, limit=limit)
    else:
        payments = crud_payment.get_multi(db, skip=skip, limit=limit)

    return [PaymentResponse.model_validate(payment) for payment in payments]


@router.put("/{payment_id}/status", response_model=PaymentResponse)
async def update_payment_status(
    payment_id: int,
    new_status: PaymentStatusEnum,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update payment status (Admin only)."""

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    payment = crud_payment.update_status(db, payment_id=payment_id, status=new_status)

    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )

    return PaymentResponse.model_validate(payment)


@router.get("/pending/count", response_model=dict)
async def get_pending_payments_count(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get count of pending payments (Admin only)."""

    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    pending_payments = crud_payment.get_pending_payments(db)

    return {"pending_count": len(pending_payments)}