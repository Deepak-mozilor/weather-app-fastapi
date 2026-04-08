from fastapi.routing import APIRouter

from weather.web.api import docs, dummy, echo, monitoring, redis
from ..view.dashboard.geocode import router as geocode_router
from ..view.login.login import router as login_router
from ..view.report.report import router as report_router
from ..view.signup.sign_up import router as signup_router


api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
api_router.include_router(geocode_router)
api_router.include_router(report_router)
api_router.include_router(login_router)
api_router.include_router(signup_router)