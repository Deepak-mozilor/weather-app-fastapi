from datetime import datetime, timedelta
from typing import Any

import bcrypt
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from jose import JWTError, jwt

from weather.db.dao.user_dao import UserDAO
from weather.db.models.user_model import User
from weather.settings import settings
from weather.web.api.login.schema import UserLogin

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"


async def verify_user_cookie(access_token: str = Cookie(None)) -> int:
    """Check if the cookie is present with the token."""
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token found. Please log in.",
        )

    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token payload.")

        return user_id

    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired or invalid."
        ) from err


router = APIRouter()


@router.post("/login")
async def send_login(
    user: UserLogin, response: Response, user_dao: UserDAO = Depends()
) -> dict[str, str]:
    """Function for user login .Creates token and store in browser."""

    db_user = await authenticate_user(user_dao, user.username, user.password)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_token({"user_id": db_user.id})

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        max_age=600,
        samesite="lax",
        secure=False,
    )

    return {"message": "login success"}


async def authenticate_user(
    user_dao: UserDAO, username: str, password: str
) -> User | None:
    """To verify the user."""

    user = await user_dao.get_user_by_username(username)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_token(data: dict[str, Any]) -> str:
    """Create token using encode ftn."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=10)

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify the password with hashed password."""
    pwd_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


@router.get("/verify-session")
async def verify_session(user_id: int = Depends(verify_user_cookie)) -> dict[str, str]:
    """Verify every 10 mins."""
    # If the bouncer lets them through, they are logged in!
    return {"status": "success", "message": "Authenticated"}
