from fastapi.routing import APIRouter

from weather.web.api import docs, echo, monitoring, redis
from weather.web.api.dashboard.view import router as geocode_router
from weather.web.api.login.view import router as login_router
from weather.web.api.report.view import router as report_router
from weather.web.api.signup.view import router as signup_router

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(geocode_router)
api_router.include_router(report_router)
api_router.include_router(login_router)
api_router.include_router(signup_router)
