from pydantic import BaseModel


class UserLogin(BaseModel):
    """Model for login."""

    username: str
    password: str
