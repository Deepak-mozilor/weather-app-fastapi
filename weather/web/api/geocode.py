import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from weather.db.dependencies import get_db_session
from weather.web.api.login import verify_user_cookie

from ...db.models.weather_model import WeatherData

__all__ = ["WeatherData"]


router = APIRouter()


class CityLocation(BaseModel):
    city: str
    latitude: float
    longitude: float


@router.post("/addtodb")
async def addtodb(
    location: CityLocation,
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(verify_user_cookie),
) -> dict:

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            api_data = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Weather API Error: {e!s}")

    current = api_data.get("current", {})

    clean_city_name = location.city.split(",")[0].strip().title()

    query = select(WeatherData).where(WeatherData.city == clean_city_name)
    result = await db.execute(query)
    existing_city = result.scalars().first()

    if existing_city:
        existing_city.time = current.get("time")
        existing_city.temperature = current.get("temperature_2m")
        existing_city.humidity = current.get("relative_humidity_2m")
        existing_city.feels = current.get("apparent_temperature")
        existing_city.wind = current.get("wind_speed_10m")
        existing_city.code = current.get("weather_code")

        db_entry = existing_city
        action = "updated"

    else:
        new_entry = WeatherData(
            time=current.get("time"),
            city=clean_city_name,
            latitude=location.latitude,
            longitude=location.longitude,
            temperature=current.get("temperature_2m"),
            humidity=current.get("relative_humidity_2m"),
            feels=current.get("apparent_temperature"),
            wind=current.get("wind_speed_10m"),
            code=current.get("weather_code"),
        )

        db.add(new_entry)
        db_entry = new_entry
        action = "added"

    try:
        await db.commit()
        await db.refresh(db_entry)

        return {
            "status": "success",
            "id": db_entry.id,
            "action": action,
            "weather": current,
        }

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Database save failed.")


@router.get("/forecast")
async def get_forcast(
    lat: float, long: float, user_id: int = Depends(verify_user_cookie)
):
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": lat,
        "longitude": long,
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "forecast_days": 5,
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            api_data = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=400, detail=f"Weather API Error: {e!s}")

    daily_forecast = api_data.get("daily", {})

    return {"status": "success", "forecast": daily_forecast}


@router.get("/cleardb")
async def clear_db(
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(verify_user_cookie),
):
    try:
        query = delete(WeatherData)

        await db.execute(query)
        await db.commit()

        return {"status": "success", "message": "Entire database wiped clean!"}

    except Exception:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to clear database.")


@router.get("/my-cities")
async def get_my_cities(
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(verify_user_cookie),
):
    try:
        query = select(WeatherData)
        result = await db.execute(query)
        saved_cities = result.scalars().all()

        return {"status": "success", "cities": saved_cities}
    except Exception:
        raise HTTPException(
            status_code=500, detail="Could not fetch cities from database"
        )
