"""
release_note.py

Модель релиз-заметок проекта.

Используется для:
- фиксации версий проекта;
- описания изменений между версиями;
- ведения истории развития продукта.

Почему это важно:
- помогает отслеживать эволюцию проекта;
- удобно для команды и пользователей;
- можно строить changelog автоматически.
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReleaseNote(Base):
    """
    Таблица релиз-заметок.

    Один проект может иметь много релизов.
    """

    __tablename__ = "release_notes"

    # ID
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # Связь с проектом
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        index=True
    )
    # Версия релиза
    version: Mapped[str] = mapped_column(String, index=True)
    # пример: "1.0.0", "1.1.2"

    # Заголовок релиза
    title: Mapped[str] = mapped_column(String)

    # Описание изменений
    description: Mapped[str] = mapped_column(String)

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    project = relationship("Project", backref="release_notes")