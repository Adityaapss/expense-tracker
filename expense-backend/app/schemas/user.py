from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Shape of the JSON body for POST /api/auth/register."""

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserLogin(BaseModel):
    """Shape of the JSON body for POST /api/auth/login."""

    email: EmailStr
    password: str


class UserOut(BaseModel):
    """What we send back to describe a user. No password_hash, ever."""

    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True  # lets us build this directly from a User ORM object


class Token(BaseModel):
    """What we send back after a successful register/login."""

    access_token: str
    token_type: str = "bearer"
