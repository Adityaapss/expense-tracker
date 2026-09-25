"""Password hashing and JWT helpers.

Keeping all of this in one file means there's exactly one place that
knows how passwords are hashed and how tokens are signed.
"""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.config import settings

ALGORITHM = "HS256"

# bcrypt only looks at the first 72 bytes of a password. Anything after
# that is silently ignored (or raises an error, depending on bcrypt
# version), so we truncate ourselves to be explicit about it.
_BCRYPT_MAX_BYTES = 72


def hash_password(plain_password: str) -> str:
    """Turn a plain-text password into a bcrypt hash to store in the database."""
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a login attempt's password against the stored hash."""
    password_bytes = plain_password.encode("utf-8")[:_BCRYPT_MAX_BYTES]
    return bcrypt.checkpw(password_bytes, password_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    """Create a signed JWT that proves 'this request is from user_id'."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Verify a token's signature and expiry, and return its payload.

    Raises jwt.PyJWTError (e.g. ExpiredSignatureError, InvalidTokenError)
    if the token is invalid, expired, or was signed with a different key.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
