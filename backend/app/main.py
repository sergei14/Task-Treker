"""
main.py

Здесь:
- создаётся экземпляр FastAPI;
- подключаются роутеры;
- настраивается логирование;
- инициализируется база данных;
- добавляются middleware (например CORS).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import setup_logging, logger
from app.db.init_db import init_db

setup_logging()

logger.info("Starting Task Tracker API...")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключение роутеров
#TODO добавим:
# from app.routers import projects, tasks, feedbacks
#
# app.include_router(projects.router, prefix="/projects", tags=["Projects"])

@app.on_event("startup")
def startup_event():
    """
    Выполняется при старте приложения.

    Здесь:
    - создаётся база данных (если её нет);
    - можно добавить кеши, подключения к сервисам и т.д.
    """

    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized successfully")

@app.get("/health")
def health_check():
    """
    Проверка, что сервис жив.

    Используется:
    - мониторингом
    - балансировщиками
    - ручной проверкой
    """

    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
    }