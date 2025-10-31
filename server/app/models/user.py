from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.database.connection import Base
from app.models.enums import RoleEnum


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(SqlEnum(RoleEnum), default=RoleEnum.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete")
    borrows = relationship("Borrow", back_populates="user", cascade="all, delete")
    payments = relationship("Payment", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User id={self.id} name='{self.name}'>"
