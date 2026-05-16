"""
project_doc.py

Модель документации проекта.

Здесь хранится расширенная информация о проекте:
- описание архитектуры;
- бизнес-логика;
- инструкции;
- внутренние заметки команды.

Почему это отдельная сущность:
- документация может быть большой;
- её удобно версионировать или расширять;
- можно разделять по разделам (pages / articles).
"""

from datetime import datetime

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProjectDoc(Base):
    """
    Документация проекта.

    Один проект может иметь несколько документов:
    - архитектура;
    - API описание;
    - гайды;
    - заметки.
    """

    __tablename__ = "project_docs"

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
    # Заголовок документа
    # =========================
    title: Mapped[str] = mapped_column(String)

    # =========================
    # Контент документа
    # =========================
    # пока простой текст, потом можно заменить на markdown/html
    content: Mapped[str] = mapped_column(String)

    # =========================
    # Метаданные
    # =========================
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )