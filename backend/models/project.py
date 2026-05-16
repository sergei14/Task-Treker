"""
project.py

Проект — это основная точка входа в систему.

Пользователь:
- заходит по ссылке или токену проекта;
- выбирает проект;
- дальше работает с задачами, фидбеком и данными внутри него.
"""

from datetime import datetime
import secrets

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

from sqlalchemy.orm import relationship

class Project(Base):
    __tablename__ = "projects"

    # =========================
    # ID
    # =========================
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # =========================
    # Публичный идентификатор
    # =========================
    # используется в URL вместо логина
    public_token: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        default=lambda: secrets.token_urlsafe(16)
    )

    # =========================
    # Основные данные
    # =========================
    name: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String, default="")

    # =========================
    # Метаданные
    # =========================
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # =========================
    # Связи
    # =========================
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    documents = relationship(
        "ProjectDoc",
        back_populates="project",
        cascade="all, delete-orphan"
    )