"""
base.py

Файл отвечает за базовую настройку работы с базой данных:
- создаёт общий ORM-класс Base для всех моделей;
- создаёт SQLAlchemy engine;
- подключает SQLite для локальной разработки;
- регистрирует модели проекта;
- создаёт таблицы при первом запуске приложения.

Модели в текущей структуре проекта находятся в папке backend/models,
поэтому импортируются через пакет models, а не через app.models.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def create_db_engine() -> Engine:
    if settings.database_url.startswith("sqlite"):
        return create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            echo=settings.debug,
        )

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        echo=settings.debug,
    )


engine = create_db_engine()


def create_tables() -> None:
    import models.attachment
    import models.feedback
    import models.project
    import models.project_doc
    import models.release_note
    import models.story_point
    import models.subtask
    import models.task

    Base.metadata.create_all(bind=engine)