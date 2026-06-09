"""
subtask.py

Модель подзадачи.

Подзадача относится к конкретной задаче и помогает разделить
большую работу на отдельные шаги.

Подзадача содержит:
- название и описание;
- статус выполнения;
- срок выполнения;
- дату создания и изменения.

При удалении основной задачи связанные подзадачи
также удаляются автоматически.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SubtaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class Subtask(Base):
    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
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

    status: Mapped[SubtaskStatus] = mapped_column(
        SqlEnum(SubtaskStatus, name="subtask_status"),
        default=SubtaskStatus.TODO,
        nullable=False,
        index=True,
    )

    deadline: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
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

    task = relationship(
        "Task",
        back_populates="subtasks",
    )