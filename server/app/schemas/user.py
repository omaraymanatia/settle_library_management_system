from pydantic import BaseModel, EmailStr
from datetime import datetime
from models.enums import RoleEnum


class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum = RoleEnum.USER


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
