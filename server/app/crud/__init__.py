"""
CRUD package for Library Management System.

This package contains CRUD (Create, Read, Update, Delete) operations
for all database models.
"""

from .user import user_crud
from .book import book_crud
from .base import CRUDBase

__all__ = [
    "user_crud",
    "book_crud",
    "CRUDBase"
]