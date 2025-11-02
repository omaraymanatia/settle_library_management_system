"""
Database seeding script for Library Management System.

This script populates the database with sample data including:
- Book classes
- Sample books
- Sample users (optional)
"""

import sys
import os
from datetime import datetime, timezone

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import get_db, engine, Base
from app.models.book_class import BookClass
from app.models.book import Book
from app.models.user import User
from app.models.enums import BookClassNameEnum, RoleEnum
from app.services.auth_service import get_password_hash


def create_book_classes(db: Session):
    """Create book classes with different pricing."""
    print("Creating book classes...")

    # Check if book classes already exist
    existing = db.query(BookClass).first()
    if existing:
        print("Book classes already exist, skipping...")
        return

    book_classes = [
        BookClass(
            name=BookClassNameEnum.A,
            borrow_fee=10.0,
            deposit_amount=5.0,
            fine_per_day=1.0
        ),
        BookClass(
            name=BookClassNameEnum.B,
            borrow_fee=15.0,
            deposit_amount=8.0,
            fine_per_day=1.5
        ),
        BookClass(
            name=BookClassNameEnum.C,
            borrow_fee=20.0,
            deposit_amount=10.0,
            fine_per_day=2.0
        )
    ]

    for book_class in book_classes:
        db.add(book_class)

    db.commit()
    print(f"Created {len(book_classes)} book classes")


def create_sample_books(db: Session):
    """Create sample books for the library."""
    print("Creating sample books...")

    # Check if books already exist
    existing = db.query(Book).first()
    if existing:
        print("Books already exist, skipping...")
        return

    # Get book classes
    class_a = db.query(BookClass).filter(BookClass.name == BookClassNameEnum.A).first()
    class_b = db.query(BookClass).filter(BookClass.name == BookClassNameEnum.B).first()
    class_c = db.query(BookClass).filter(BookClass.name == BookClassNameEnum.C).first()

    if not all([class_a, class_b, class_c]):
        print("Book classes not found. Please create book classes first.")
        return

    sample_books = [
        # Fiction & Literature (Class A)
        Book(
            isbn="9780451524935",
            title="1984",
            author="George Orwell",
            shelf_location="Fiction-A1",
            total_quantity=5,
            available_quantity=5,
            book_class_id=class_a.id
        ),
        Book(
            isbn="9780062315007",
            title="The Alchemist",
            author="Paulo Coelho",
            shelf_location="Fiction-A2",
            total_quantity=3,
            available_quantity=3,
            book_class_id=class_a.id
        ),
        Book(
            isbn="9780060935467",
            title="To Kill a Mockingbird",
            author="Harper Lee",
            shelf_location="Fiction-A3",
            total_quantity=4,
            available_quantity=4,
            book_class_id=class_a.id
        ),
        Book(
            isbn="9780743273565",
            title="The Great Gatsby",
            author="F. Scott Fitzgerald",
            shelf_location="Fiction-A4",
            total_quantity=6,
            available_quantity=6,
            book_class_id=class_a.id
        ),
        Book(
            isbn="9780140283334",
            title="Pride and Prejudice",
            author="Jane Austen",
            shelf_location="Fiction-A5",
            total_quantity=3,
            available_quantity=3,
            book_class_id=class_a.id
        ),

        # Technology & Programming (Class B)
        Book(
            isbn="9780134685991",
            title="Effective Python",
            author="Brett Slatkin",
            shelf_location="Tech-B1",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_b.id
        ),
        Book(
            isbn="9781449355739",
            title="Learning Python",
            author="Mark Lutz",
            shelf_location="Tech-B2",
            total_quantity=4,
            available_quantity=4,
            book_class_id=class_b.id
        ),
        Book(
            isbn="9780134757599",
            title="Refactoring",
            author="Martin Fowler",
            shelf_location="Tech-B3",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_b.id
        ),
        Book(
            isbn="9780135957059",
            title="The Pragmatic Programmer",
            author="David Thomas, Andrew Hunt",
            shelf_location="Tech-B4",
            total_quantity=3,
            available_quantity=3,
            book_class_id=class_b.id
        ),
        Book(
            isbn="9781617294136",
            title="Grokking Algorithms",
            author="Aditya Bhargava",
            shelf_location="Tech-B5",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_b.id
        ),

        # Science & Research (Class C)
        Book(
            isbn="9780393347777",
            title="Sapiens",
            author="Yuval Noah Harari",
            shelf_location="Science-C1",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_c.id
        ),
        Book(
            isbn="9780553380163",
            title="A Brief History of Time",
            author="Stephen Hawking",
            shelf_location="Science-C2",
            total_quantity=3,
            available_quantity=3,
            book_class_id=class_c.id
        ),
        Book(
            isbn="9780385537859",
            title="The Gene: An Intimate History",
            author="Siddhartha Mukherjee",
            shelf_location="Science-C3",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_c.id
        ),
        Book(
            isbn="9780062316097",
            title="Homo Deus",
            author="Yuval Noah Harari",
            shelf_location="Science-C4",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_c.id
        ),
        Book(
            isbn="9780544947979",
            title="The Hidden Reality",
            author="Brian Greene",
            shelf_location="Science-C5",
            total_quantity=1,
            available_quantity=1,
            book_class_id=class_c.id
        ),

        # Additional Popular Books (Mixed Classes)
        Book(
            isbn="9780307887436",
            title="Ready Player One",
            author="Ernest Cline",
            shelf_location="Fiction-A6",
            total_quantity=4,
            available_quantity=4,
            book_class_id=class_a.id
        ),
        Book(
            isbn="9780385121675",
            title="The Catcher in the Rye",
            author="J.D. Salinger",
            shelf_location="Fiction-A7",
            total_quantity=3,
            available_quantity=3,
            book_class_id=class_a.id
        ),
        Book(
            isbn="9781449331818",
            title="JavaScript: The Good Parts",
            author="Douglas Crockford",
            shelf_location="Tech-B6",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_b.id
        ),
        Book(
            isbn="9780596520687",
            title="JavaScript: The Definitive Guide",
            author="David Flanagan",
            shelf_location="Tech-B7",
            total_quantity=3,
            available_quantity=3,
            book_class_id=class_b.id
        ),
        Book(
            isbn="9780735619678",
            title="Code Complete",
            author="Steve McConnell",
            shelf_location="Tech-B8",
            total_quantity=2,
            available_quantity=2,
            book_class_id=class_b.id
        )
    ]

    for book in sample_books:
        db.add(book)

    db.commit()
    print(f"Created {len(sample_books)} sample books")


def create_sample_users(db: Session):
    """Create sample users (optional)."""
    print("Creating sample users...")

    # Check if users already exist
    existing = db.query(User).first()
    if existing:
        print("Users already exist, skipping...")
        return

    sample_users = [
        User(
            name="Admin User",
            email="admin@library.com",
            password=get_password_hash("admin123"),
            role=RoleEnum.ADMIN
        ),
        User(
            name="Librarian",
            email="librarian@library.com",
            password=get_password_hash("librarian123"),
            role=RoleEnum.LIBRARIAN
        ),
        User(
            name="John Doe",
            email="john@example.com",
            password=get_password_hash("user123"),
            role=RoleEnum.USER
        ),
        User(
            name="Jane Smith",
            email="jane@example.com",
            password=get_password_hash("user123"),
            role=RoleEnum.USER
        )
    ]

    for user in sample_users:
        db.add(user)

    db.commit()
    print(f"Created {len(sample_users)} sample users")


def main():
    """Main function to seed the database."""
    print("🌱 Starting database seeding...")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Get database session
    db = next(get_db())

    try:
        # Create data in order (due to foreign key constraints)
        create_book_classes(db)
        create_sample_books(db)
        create_sample_users(db)

        print("✅ Database seeding completed successfully!")
        print("\nSample data created:")
        print("- 3 Book classes (A, B, C)")
        print("- 20 Sample books across different categories")
        print("- 4 Sample users (admin, librarian, 2 regular users)")
        print("\nSample login credentials:")
        print("Admin: admin@library.com / admin123")
        print("Librarian: librarian@library.com / librarian123")
        print("User: john@example.com / user123")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()