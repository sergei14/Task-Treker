"""
init_db.py

Этот файл отвечает за первичную инициализацию базы данных.

Что он делает:
- создаёт SQLite-файл, если его ещё нет;
- создаёт все таблицы по ORM-моделям;
- позволяет запускать проект без внешней БД;
- используется только в dev/test режиме.

Важно:
- в production используется Alembic, а не create_all
"""

import logging

from app.db.base import create_tables

logger = logging.getLogger("tracker.db")


def init_db() -> None:
    """
    Инициализирует базу данных.

    Выполняет:
    - создание всех таблиц;
    - логирование процесса;
    - безопасный запуск при старте приложения.
    """

    logger.info("Инициализация базы данных...")

    try:
        create_tables()
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.exception(f"Ошибка инициализации БД: {e}")
        raise