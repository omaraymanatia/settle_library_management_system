from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from app.db.session import Base
from .enums import BookClassNameEnum


class BookClass(Base):
    __tablename__ = "book_classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(SqlEnum(BookClassNameEnum), nullable=False, unique=True)
    borrow_fee = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    fine_per_day = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # relationships
    books = relationship("Book", back_populates="book_class", cascade="all, delete")

    def __repr__(self):
        return f"<BookClass name='{self.name}'>"
