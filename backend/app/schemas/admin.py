from pydantic import BaseModel, EmailStr
from typing import Optional


class AdminVerifyPassword(BaseModel):
    password: str


class AdminInfo(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    email2: Optional[str] = None  # Second email for sending emails
    phone: Optional[str] = None
    has_custom_password: bool  # True if password_hash is set, False if using default

    class Config:
        from_attributes = True


class AdminUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    email2: Optional[EmailStr] = None  # Second email for sending emails
    phone: Optional[str] = None
    new_password: Optional[str] = None


class AdminVerifyResponse(BaseModel):
    success: bool
    message: str

