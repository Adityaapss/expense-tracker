"""Register/login business logic. Routers call these; they don't touch
the database or password hashing directly.
"""
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.models import User
from app.schemas.user import UserCreate, UserLogin


def register_user(db: Session, data: UserCreate) -> User:
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)  # loads id, created_at that the database generated
    return user


def authenticate_user(db: Session, data: UserLogin) -> User:
    user = db.scalar(select(User).where(User.email == data.email))

    # Deliberately the same error whether the email doesn't exist or the
    # password is wrong, so a caller can't use this to guess which
    # emails are registered.
    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )

    if user is None:
        raise invalid_credentials
    if not verify_password(data.password, user.password_hash):
        raise invalid_credentials

    return user
