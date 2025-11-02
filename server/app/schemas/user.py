from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from models.enums import RoleEnum


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum = RoleEnum.USER


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleEnum] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
