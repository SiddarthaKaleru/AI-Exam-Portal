"""User document helpers for MongoDB."""

from datetime import datetime, timezone


def create_user_doc(name: str, email: str, password_hash: str, role: str = "student") -> dict:
    """Create a user document for MongoDB insertion."""
    return {
        "name": name,
        "email": email,
        "password_hash": password_hash,
        "role": role,  # "admin" or "student"
        "created_at": datetime.now(timezone.utc),
    }
