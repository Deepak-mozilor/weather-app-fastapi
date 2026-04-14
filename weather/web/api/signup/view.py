from typing import Any

import bcrypt
from fastapi import APIRouter, Depends

from weather.db.dao.user_dao import UserDAO
from weather.web.api.signup.schema import UserLogin

router = APIRouter()


@router.post("/signup")
async def sign_up(user: UserLogin, user_dao: UserDAO = Depends()) -> dict[str, Any]:
    """Route function for signup logic."""

    hashed_pwd = hashed(user.password)

    new_entry = await user_dao.create_user(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pwd,
    )

    return {"message": "User created successfully", "user_id": new_entry.id}


def hashed(password: str) -> str:
    """Convert password to hash."""
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password with encypted password."""
    pwd_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)
