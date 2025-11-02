"""
API package for Library Management System.

This package contains all API route modules.
"""

from .user import router as user_router
from .auth import router as auth_router
from .book import router as book_router
from .borrow import router as borrow_router
from .payment import router as payment_router
from .reservation import router as reservation_router

__all__ = [
    "user_router",
    "auth_router",
    "book_router",
    "borrow_router",
    "payment_router",
    "reservation_router"
]