from pydantic import BaseModel


class CityRequest(BaseModel):
    """Model for city."""

    city: str
