"""
API package for Library Management System.

This package contains all API route modules.
"""

from .user import router as user_router
from .auth import router as auth_router

__all__ = ["user_router", "auth_router"]