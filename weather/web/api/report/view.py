from typing import Any

from fastapi import APIRouter, Depends

from weather.db.dao.weather_data_dao import WeatherDAO
from weather.web.api.login.view import verify_user_cookie
from weather.web.api.report.schema import CityRequest

router = APIRouter()


@router.post("/report")
async def get_report(
    request: CityRequest,
    weather_dao: WeatherDAO = Depends(),
    user_id: int = Depends(verify_user_cookie),
) -> list[Any]:
    """Route to get report."""

    return await weather_dao.get_city_report(city=request.city)


@router.get("/cities")
async def get_cities(
    weather_dao: WeatherDAO = Depends(),
    user_id: int = Depends(verify_user_cookie),
) -> list[Any]:
    """Fetch all cities."""

    return await weather_dao.get_all_distinct_cities()
