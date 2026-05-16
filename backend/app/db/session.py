"""
session.py

Этот файл отвечает за создание и управление сессиями базы данных.

Что здесь находится:
- engine (подключение к базе данных);
- SessionLocal (фабрика сессий);
- dependency для FastAPI.

Почему это важно:
- каждая операция с БД должна выполняться через сессию;
- FastAPI использует dependency injection для управления соединениями;
- позволяет безопасно работать с транзакциями.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.db.base import engine


# =========================
# Session factory
# =========================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,   # не коммитим автоматически изменения
    autocommit=False,  # ручное управление транзакциями
    expire_on_commit=False,  # не инвалидируем объекты после commit
)


def get_db() -> Session:
    """
    Dependency для FastAPI.

    Используется в роутерах:

        @router.get("/")
        def get_items(db: Session = Depends(get_db)):

    Что делает:
    - создаёт новую сессию;
    - отдаёт её в endpoint;
    - гарантированно закрывает после использования.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()