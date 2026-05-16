"""
feedback.py

Модель обратной связи.

Теперь фидбек:
- принадлежит конкретному проекту;
- может быть создан без авторизации;
- доступен через token;
- может содержать баги / пожелания / кейсы.
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Feedback(Base):
    """
    Таблица фидбеков проекта.
    """

    __tablename__ = "feedbacks"

    # =========================
    # ID
    # =========================
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # =========================
    # Связь с проектом
    # =========================
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        index=True
    )

    # =========================
    # Токен доступа
    # =========================
    # используется для доступа без авторизации (например, форма)
    token: Mapped[str] = mapped_column(String, index=True)

    # =========================
    # Тип фидбека
    # =========================
    # bug / feature / case
    type: Mapped[str] = mapped_column(String, index=True)

    # =========================
    # Данные пользователя
    # =========================
    full_name: Mapped[str] = mapped_column(String)
    direction: Mapped[str] = mapped_column(String)

    # =========================
    # Контент
    # =========================
    comment: Mapped[str] = mapped_column(String)

    # =========================
    # Метаданные
    # =========================
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )