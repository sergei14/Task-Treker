"""
task.py

Модель задачи проекта.

Задача относится к конкретному проекту и содержит:
- название и описание работы;
- статус выполнения;
- приоритет;
- срок выполнения;
- подзадачи;
- оценку в сторипоинтах.

Внутри одного проекта может быть несколько задач.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    status: Mapped[TaskStatus] = mapped_column(
        SqlEnum(TaskStatus, name="task_status"),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
    )

    priority: Mapped[TaskPriority] = mapped_column(
        SqlEnum(TaskPriority, name="task_priority"),
        default=TaskPriority.MEDIUM,
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

    project = relationship(
        "Project",
        back_populates="tasks",
    )

    subtasks = relationship(
        "Subtask",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    story_point = relationship(
        "StoryPoint",
        back_populates="task",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )