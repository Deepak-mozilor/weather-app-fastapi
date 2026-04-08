from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from weather.db.dependencies import get_db_session
from weather.db.models.weather_model import WeatherData
from weather.web.api.view.login.login import verify_user_cookie

router = APIRouter()


class CityRequest(BaseModel):
    city: str


@router.post("/report")
async def get_report(
    request: CityRequest,
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(verify_user_cookie),
):

    search_city = request.city

    query = select(WeatherData).where(WeatherData.city == search_city)
    result = await db.execute(query)

    report = result.scalars().all()

    return report


@router.get("/cities")
async def get_cities(
    db: AsyncSession = Depends(get_db_session),
    user_id: int = Depends(verify_user_cookie),
):
    query = select(WeatherData.city).distinct()
    result = await db.execute(query)

    cities = result.scalars().all()

    return cities
