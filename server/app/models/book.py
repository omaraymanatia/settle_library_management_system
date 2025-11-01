from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from server.app.db.session import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    isbn = Column(String(20), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    shelf_location = Column(String(100))
    total_quantity = Column(Integer, nullable=False)
    available_quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    book_class_id = Column(Integer, ForeignKey("book_classes.id", ondelete="SET NULL"))

    # relationships
    book_class = relationship("BookClass", back_populates="books")
    reservations = relationship("Reservation", back_populates="book", cascade="all, delete")
    borrows = relationship("Borrow", back_populates="book", cascade="all, delete")

    def __repr__(self):
        return f"<Book title='{self.title}' isbn='{self.isbn}'>"
