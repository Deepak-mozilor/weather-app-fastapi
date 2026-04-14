from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    """Model for login."""

    email: EmailStr
    username: str
    password: str
