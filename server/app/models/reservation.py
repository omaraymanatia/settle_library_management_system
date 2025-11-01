from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from server.app.db.session import Base
from .enums import ReservationStatusEnum


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    reservation_date = Column(DateTime, default=datetime.utcnow)
    expiry_date = Column(DateTime, nullable=False)
    status = Column(SqlEnum(ReservationStatusEnum), default=ReservationStatusEnum.RESERVED)

    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    payment_id = Column(Integer, ForeignKey("payments.id", ondelete="SET NULL"))

    # relationships
    book = relationship("Book", back_populates="reservations")
    user = relationship("User", back_populates="reservations")
    payment = relationship("Payment", back_populates="reservations")
    borrows = relationship("Borrow", back_populates="reservation")

    def __repr__(self):
        return f"<Reservation id={self.id} status='{self.status}'>"
