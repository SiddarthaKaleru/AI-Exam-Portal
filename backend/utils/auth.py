"""JWT and password utilities."""

from datetime import datetime, timedelta, timezone
import jwt
import bcrypt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_HOURS

security = HTTPBearer()


# ─── Password Hashing ───────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password with bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT Tokens ──────────────────────────────────────────────────────

def create_token(user_id: str, email: str, role: str) -> str:
    """Create a JWT token."""
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """FastAPI dependency — extract current user from JWT Bearer token."""
    return decode_token(credentials.credentials)


def require_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """FastAPI dependency — require admin role."""
    user = decode_token(credentials.credentials)
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
