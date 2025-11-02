"""
Database verification script - Check what data exists in the database.
"""

import sys
import os

# Add the parent directory to sys.path to import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.book_class import BookClass
from app.models.book import Book
from app.models.user import User


def check_database_contents():
    """Check and display database contents."""
    print("📊 Checking database contents...\n")

    db = next(get_db())

    try:
        # Check book classes
        book_classes = db.query(BookClass).all()
        print(f"📚 Book Classes ({len(book_classes)}):")
        for bc in book_classes:
            print(f"  - {bc.name}: Borrow Fee ${bc.borrow_fee}, Deposit ${bc.deposit_amount}, Fine ${bc.fine_per_day}/day")

        # Check books
        books = db.query(Book).all()
        print(f"\n📖 Books ({len(books)}):")
        for book in books:
            class_name = book.book_class.name if book.book_class else "No Class"
            print(f"  - '{book.title}' by {book.author}")
            print(f"    ISBN: {book.isbn} | Available: {book.available_quantity}/{book.total_quantity} | Class: {class_name}")
            print(f"    Location: {book.shelf_location}")
            print()

        # Check users
        users = db.query(User).all()
        print(f"👥 Users ({len(users)}):")
        for user in users:
            print(f"  - {user.name} ({user.email}) - Role: {user.role}")

        print(f"\n✅ Database contains:")
        print(f"   📚 {len(book_classes)} book classes")
        print(f"   📖 {len(books)} books")
        print(f"   👥 {len(users)} users")

    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    check_database_contents()