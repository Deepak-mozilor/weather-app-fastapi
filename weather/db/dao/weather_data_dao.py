from typing import Any

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from weather.db.dependencies import get_db_session
from weather.db.models.weather_data_model import WeatherData


class WeatherDAO:
    """Data Access Object for WeatherData records."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)) -> None:
        self.session = session

    async def upsert_city_weather(
        self,
        user_id: int,
        city: str,
        lat: float,
        lon: float,
        weather_data: dict[str, Any],
    ) -> tuple[WeatherData, str]:
        """Updates a city's weather if it exists, or inserts a new one."""

        query = select(WeatherData).where(
            WeatherData.city == city, WeatherData.user_id == user_id
        )
        result = await self.session.execute(query)
        existing_city = result.scalars().first()

        if existing_city:
            # Update existing
            existing_city.time = str(weather_data.get("time", ""))
            existing_city.temperature = float(weather_data.get("temperature_2m", 0.0))
            existing_city.humidity = int(weather_data.get("relative_humidity_2m", 0))
            existing_city.feels = float(weather_data.get("apparent_temperature", 0.0))
            existing_city.wind = int(weather_data.get("wind_speed_10m", 0))
            existing_city.code = int(weather_data.get("weather_code", 0))

            action = "updated"
            db_entry = existing_city
        else:
            db_entry = WeatherData(
                time=str(weather_data.get("time", "")),
                city=city,
                latitude=lat,
                longitude=lon,
                temperature=float(weather_data.get("temperature_2m", 0.0)),
                humidity=int(weather_data.get("relative_humidity_2m", 0)),
                feels=float(weather_data.get("apparent_temperature", 0.0)),
                wind=int(weather_data.get("wind_speed_10m", 0)),
                code=int(weather_data.get("weather_code", 0)),
                user_id=user_id,
            )
            self.session.add(db_entry)
            action = "added"

        await self.session.commit()
        await self.session.refresh(db_entry)

        return db_entry, action

    async def get_user_cities(self, user_id: int) -> list[WeatherData]:
        """Fetches all saved cities for a specific user."""
        query = select(WeatherData).where(WeatherData.user_id == user_id)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def clear_user_cities(self, user_id: int) -> None:
        """Deletes all saved cities for a specific user."""
        query = delete(WeatherData).where(WeatherData.user_id == user_id)
        await self.session.execute(query)
        await self.session.commit()

    async def get_city_report(self, city: str) -> list[WeatherData]:
        """Fetches all weather records for a specific search city."""
        query = select(WeatherData).where(WeatherData.city == city)
        result = await self.session.execute(query)

        return list(result.scalars().all())

    async def get_all_distinct_cities(self) -> list[str]:
        """Fetches a list of all unique cities in the database."""
        query = select(WeatherData.city).distinct()
        result = await self.session.execute(query)

        return list(result.scalars().all())
