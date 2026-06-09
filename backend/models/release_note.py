"""
release_note.py

Модель релизных заметок проекта.

Релизноты используются для хранения истории изменений проекта:
- версии релиза;
- названия обновления;
- описания новых функций, исправлений и изменений.

Один проект может содержать несколько релизнотов,
но версия релиза внутри одного проекта не должна повторяться.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ReleaseNote(Base):
    __tablename__ = "release_notes"
    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "version",
            name="uq_release_note_project_version",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="release_notes",
    )