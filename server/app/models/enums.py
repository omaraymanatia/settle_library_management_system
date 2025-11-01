from enum import Enum

class RoleEnum(str, Enum):
    USER = "user"
    ADMIN = "admin"


class BookClassNameEnum(str, Enum):
    A = "A"
    B = "B"
    C = "C"


class ReservationStatusEnum(str, Enum):
    PENDING = "pending"
    RESERVED = "reserved"
    BORROWED = "borrowed"
    EXPIRED = "expired"


class BorrowStatusEnum(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    REJECTED = "rejected"
    BORROWED = "borrowed"
    RETURN_PENDING = "return_pending"
    RETURNED = "returned"
    LATE = "late"


class PaymentTypeEnum(str, Enum):
    DEPOSIT = "deposit"
    BORROW_FEE = "borrow_fee"
    FINE = "fine"


class PaymentStatusEnum(str, Enum):
    PAID = "paid"
    PENDING = "pending"