from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles

from weather.web.api.geocode import router as geocode_router
from weather.web.api.login import router as login_router
from weather.web.api.report import router as report_router
from weather.web.api.router import api_router
from weather.web.api.sign_up import router as signup_router
from weather.web.lifespan import lifespan_setup

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="weather",
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5501",
            "http://localhost:5501",
            "http://127.0.0.1:5502",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")
    app.include_router(geocode_router)
    app.include_router(report_router)
    app.include_router(login_router)
    app.include_router(signup_router)

    # Adds static directory.
    # This directory is used to access swagger files.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")

    return app
