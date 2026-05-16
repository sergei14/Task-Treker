"""
base.py

Этот файл нужен для базовой настройки слоя базы данных.

Что здесь находится:
- общий declarative Base для всех ORM-моделей;
- функция создания SQLAlchemy engine;
- функция для автоматического создания таблиц в SQLite;
- логика поддержки будущего перехода на внешнюю БД (PostgreSQL и др.).

Почему это важно:
- все модели наследуются от одного Base;
- приложение может стартовать без внешнего сервера БД;
- легко переключиться на production-базу без переписывания кода.
"""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Базовый класс для всех ORM-моделей проекта.

    Все модели должны наследоваться отсюда:

        class Project(Base):
            __tablename__ = "projects"
    """
    pass


def get_database_path() -> Path:
    """
    Возвращает путь к SQLite-файлу базы данных.

    Используется только если database_url указывает на SQLite.

    Пример:
        sqlite:///./tracker.db → backend/tracker.db
    """

    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        # убираем префикс sqlite:/// и получаем путь
        relative_path = db_url.replace("sqlite:///", "", 1)
        return settings.base_dir / relative_path

    # fallback (если вдруг не sqlite)
    return settings.base_dir / "tracker.db"


def create_db_engine():
    """
    Создаёт SQLAlchemy engine.

    Поддерживает:
    - SQLite (локально, dev режим)
    - PostgreSQL / внешние БД (future-ready)

    Важно:
    - SQLite требует check_same_thread=False для FastAPI
    """
    db_url = settings.database_url

    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
        )

    # для будущего Postgres / MySQL
    return create_engine(db_url, pool_pre_ping=True)


engine = create_db_engine()


def create_tables() -> None:
    """
    Создаёт таблицы в базе данных.

    Используется только в dev режиме.

    Важно:
    - все модели должны быть импортированы до вызова create_all,
      иначе SQLAlchemy их не зарегистрирует.
    """

    # импорт моделей обязателен для регистрации metadata
    from app.models import (  # noqa: F401
        attachment,
        feedback,
        project,
        project_doc,
        release_note,
        story_point,
        subtask,
        task,
    )

    Base.metadata.create_all(bind=engine)