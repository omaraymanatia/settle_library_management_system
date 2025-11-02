from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SqlEnum
from sqlalchemy.orm import relationship
from db.session import Base
from .enums import PaymentTypeEnum, PaymentStatusEnum


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    payment_type = Column(SqlEnum(PaymentTypeEnum), nullable=False)
    status = Column(SqlEnum(PaymentStatusEnum), default=PaymentStatusEnum.PENDING)
    payment_date = Column(DateTime, default=datetime.now(timezone.utc))

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))

    # relationships
    user = relationship("User", back_populates="payments")
    reservations = relationship("Reservation", back_populates="payment")
    borrows = relationship("Borrow", back_populates="payment")

    def __repr__(self):
        return f"<Payment id={self.id} type='{self.payment_type}' status='{self.status}'>"
