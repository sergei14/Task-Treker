"""
init_db.py

Файл отвечает за первичную инициализацию базы данных:
- запускает создание таблиц по ORM-моделям;
- используется при старте FastAPI-приложения;
- записывает информацию об успешном запуске или ошибке в лог.

Для текущей версии проекта таблицы создаются автоматически.
В дальнейшем при переходе к production-режиму вместо create_all
лучше будет использовать миграции Alembic.
"""

from app.core.logger import logger
from app.db.base import create_tables


def init_db() -> None:
    try:
        create_tables()
        logger.info("Database tables initialized successfully")
    except Exception:
        logger.exception("Database initialization failed")
        raise