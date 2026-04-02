import bcrypt
from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from weather.db.dependencies import get_db_session
from weather.db.models.user_model import User


class UserLogin(BaseModel):
    email: EmailStr
    username: str
    password: str


router = APIRouter()


@router.post("/signup")
async def sign_up(user: UserLogin, db: AsyncSession = Depends(get_db_session)):

    new_entry = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed(user.password),
    )

    db.add(new_entry)
    await db.commit()
    await db.refresh(new_entry)

    return {"message": "User created successfully", "user_id": new_entry.id}


def hashed(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)
