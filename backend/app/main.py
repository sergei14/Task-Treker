"""
main.py

Главный файл FastAPI-приложения.

Здесь:
- создаётся экземпляр приложения;
- настраивается CORS;
- при запуске инициализируется база данных;
- подключаются роутеры проектов, задач, фидбеков и файлов;
- подключается минимальный frontend-интерфейс;
- доступны служебные маршруты для проверки работы API.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.logger import logger, setup_logging
from app.db.init_db import init_db
from routers import feedbacks, files, projects, tasks


setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Starting %s...", settings.app_name)
    logger.info("Initializing database...")

    init_db()

    logger.info("Database initialized successfully")

    yield

    logger.info("Stopping %s...", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials="*" not in settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(projects.router, prefix=settings.api_prefix)
app.include_router(tasks.router, prefix=settings.api_prefix)
app.include_router(feedbacks.router, prefix=settings.api_prefix)
app.include_router(files.router, prefix=settings.api_prefix)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "frontend": "/ui",
        "docs": "/docs",
    }


@app.get("/ui", include_in_schema=False)
def frontend() -> FileResponse:
    index_file = settings.base_dir / "front" / "index.html"

    if not index_file.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Frontend-файл не найден",
        )

    return FileResponse(index_file)


@app.get("/health", tags=["System"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }