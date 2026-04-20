"""Authentication routes — register and login."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from database import get_database
from models.user import create_user_doc
from utils.auth import hash_password, verify_password, create_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# ─── Request Schemas ─────────────────────────────────────────────────

ADMIN_SECRET_KEY = "123456"


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"  # "admin" or "student"
    adminSecret: str = ""


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ─── Endpoints ───────────────────────────────────────────────────────

@router.post("/register")
async def register(req: RegisterRequest):
    """Register a new user."""
    db = get_database()

    # Validate admin secret key
    if req.role == "admin" and req.adminSecret != ADMIN_SECRET_KEY:
        raise HTTPException(status_code=403, detail="Invalid admin secret key")

    # Check if email already exists
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    user_doc = create_user_doc(
        name=req.name,
        email=req.email,
        password_hash=hash_password(req.password),
        role=req.role,
    )
    result = await db.users.insert_one(user_doc)

    # Generate JWT
    token = create_token(
        user_id=str(result.inserted_id),
        email=req.email,
        role=req.role,
    )

    return {
        "message": "Registration successful",
        "token": token,
        "user": {
            "id": str(result.inserted_id),
            "name": req.name,
            "email": req.email,
            "role": req.role,
        },
    }


@router.post("/login")
async def login(req: LoginRequest):
    """Login with email and password."""
    db = get_database()

    user = await db.users.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(
        user_id=str(user["_id"]),
        email=user["email"],
        role=user["role"],
    )

    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
        },
    }
