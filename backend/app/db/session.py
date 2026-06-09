"""
session.py

Файл отвечает за управление подключениями к базе данных:
- создаёт фабрику SQLAlchemy-сессий;
- предоставляет dependency get_db() для FastAPI-роутеров;
- закрывает соединение после выполнения запроса;
- откатывает изменения при возникновении ошибки.

Все операции с проектами, задачами, документацией,
релизнотами и фидбеками будут выполняться через эту сессию.
"""

from collections.abc import Generator

from sqlalchemy.orm import Session, sessionmaker

from app.db.base import engine


SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()