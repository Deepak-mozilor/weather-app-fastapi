from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Float, Integer, String

from weather.db.base import Base


class WeatherData(Base):
    """Model for demo purpose."""

    __tablename__ = "weather_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)

    time: Mapped[str] = mapped_column(String(length=200))
    city: Mapped[str] = mapped_column(String(length=200), nullable=False)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[int] = mapped_column(Integer)
    feels: Mapped[float] = mapped_column(Float)
    wind: Mapped[int] = mapped_column(Integer)
    code: Mapped[int] = mapped_column(Integer)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)

    __table_args__ = (UniqueConstraint("user_id", "city", name="uq_user_city"),)
    user: Mapped["User"] = relationship(back_populates="weather_data") # pyright: ignore[reportUndefinedVariable]  # noqa: F821

