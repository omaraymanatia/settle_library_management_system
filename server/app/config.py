"""
Simple application configuration module.
Loads environment variables from .env file.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL")

# Security Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Application Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Reservation Configuration
RESERVATION_EXPIRY_HOURS = int(os.getenv("RESERVATION_EXPIRY_HOURS", "24"))
DEPOSIT_PERCENTAGE = float(os.getenv("DEPOSIT_PERCENTAGE", "0.1"))


class Settings:
    """Settings class to access configuration values."""
    DATABASE_URL = DATABASE_URL
    SECRET_KEY = SECRET_KEY
    JWT_ALGORITHM = JWT_ALGORITHM
    ACCESS_TOKEN_EXPIRE_MINUTES = ACCESS_TOKEN_EXPIRE_MINUTES
    DEBUG = DEBUG
    ENVIRONMENT = ENVIRONMENT
    RESERVATION_EXPIRY_HOURS = RESERVATION_EXPIRY_HOURS
    DEPOSIT_PERCENTAGE = DEPOSIT_PERCENTAGE


settings = Settings()
