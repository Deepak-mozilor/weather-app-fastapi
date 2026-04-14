from pydantic import BaseModel, ConfigDict


class CityLocation(BaseModel):
    """Model for city data."""

    city: str
    latitude: float
    longitude: float


class WeatherDataResponse(BaseModel):
    """Response model for /my-cities."""

    id: int
    user_id : int
    time: str
    city: str
    temperature: float
    humidity: int
    feels: float
    wind: int
    code: int
    # These are nullable in your DB, so we allow None in Pydantic
    longitude: float | None = None
    latitude: float | None = None

    # Crucial step: Tells Pydantic to read from SQLAlchemy ORM models
    model_config = ConfigDict(from_attributes=True)
