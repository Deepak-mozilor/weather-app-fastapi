from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException

from weather.db.dao.weather_data_dao import WeatherDAO
from weather.db.models.weather_data_model import WeatherData
from weather.web.api.dashboard.schema import CityLocation, WeatherDataResponse
from weather.web.api.login.view import verify_user_cookie

router = APIRouter()


@router.post("/addtodb")
async def addtodb(
    location: CityLocation,
    weather_dao: WeatherDAO = Depends(),
    user_id: int = Depends(verify_user_cookie),
) -> dict[str, Any]:
    """Main route i.e dashboard route."""

    url = "https://api.open-meteo.com/v1/forecast"
    params: dict[str, Any] = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,"
            "apparent_temperature,wind_speed_10m,weather_code"
        ),
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            api_data = response.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=400, detail=f"Weather API Error: {e!s}"
            ) from e

    current = api_data.get("current", {})

    clean_city_name = location.city.split(",")[0].strip().title()

    try:
        db_entry, action = await weather_dao.upsert_city_weather(
            user_id=user_id,
            city=clean_city_name,
            lat=location.latitude,
            lon=location.longitude,
            weather_data=current,
        )

        return {
            "status": "success",
            "id": db_entry.id,
            "action": action,
            "weather": current,
        }

    except Exception as err:
        raise HTTPException(status_code=500, detail="Database save failed.") from err


@router.get("/forecast")
async def get_forcast(
    lat: float, long: float, user_id: int = Depends(verify_user_cookie)
) -> dict[str, Any]:
    """Forcast data retrieval route."""
    url = "https://api.open-meteo.com/v1/forecast"

    params: dict[str, float | int | str] = {
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
            raise HTTPException(
                status_code=400, detail=f"Weather API Error: {e!s}"
            ) from e

    daily_forecast = api_data.get("daily", {})

    return {"status": "success", "forecast": daily_forecast}


@router.get("/cleardb")
async def clear_db(
    weather_dao: WeatherDAO = Depends(),
    user_id: int = Depends(verify_user_cookie),
) -> dict[str, Any]:
    """Clear button route to clear the db."""
    try:
        await weather_dao.clear_user_cities(user_id=user_id)
        return {"status": "success", "message": "Entire database wiped clean!"}

    except Exception as err:
        raise HTTPException(
            status_code=500, detail="Failed to clear database."
        ) from err


@router.get("/my-cities", response_model=list[WeatherDataResponse])
async def get_my_cities(
    weather_dao: WeatherDAO = Depends(),
    user_id: int = Depends(verify_user_cookie),
) -> list[WeatherData]:
    """Get the city of the user."""
    try:
        return await weather_dao.get_user_cities(user_id=user_id)

    except Exception as err:
        raise HTTPException(
            status_code=500, detail="Could not fetch cities from database"
        ) from err
