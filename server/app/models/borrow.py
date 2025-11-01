from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from database.connection import Base
from .enums import BorrowStatusEnum


class Borrow(Base):
    __tablename__ = "borrows"

    id = Column(Integer, primary_key=True, index=True)
    borrow_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime, nullable=False)
    return_date = Column(DateTime, nullable=True)
    status = Column(SqlEnum(BorrowStatusEnum), default=BorrowStatusEnum.PENDING_APPROVAL)

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    reservation_id = Column(Integer, ForeignKey("reservations.id", ondelete="SET NULL"))
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"))

    # relationships
    book = relationship("Book", back_populates="borrows")
    user = relationship("User", back_populates="borrows")
    reservation = relationship("Reservation", back_populates="borrows")
    payment = relationship("Payment", back_populates="borrows")

    def __repr__(self):
        return f"<Borrow id={self.id} status='{self.status}'>"
