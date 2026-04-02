from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Float, Integer, String

from weather.db.base import Base


class WeatherData(Base):
    """Model for demo purpose."""

    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    time: Mapped[str] = mapped_column(String(length=200))
    city: Mapped[str] = mapped_column(String(length=200), unique=True)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[int] = mapped_column(Integer)
    feels: Mapped[float] = mapped_column(Float)
    wind: Mapped[int] = mapped_column(Integer)
    code: Mapped[int] = mapped_column(Integer)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
