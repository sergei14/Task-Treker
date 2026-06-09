"""
project.py

Модель проекта — основной сущности трекера.

Проект содержит:
- название и описание;
- публичный токен для доступа;
- статус проекта: текущий, завершённый или архивный;
- документацию;
- релизноты;
- задачи;
- фидбеки.

Через проект пользователь получает доступ ко всей информации
о работе: текущим задачам, подзадачам, оценкам, изменениям
и обратной связи.
"""
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from utils.token_parser import generate_public_token

class ProjectStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    public_token: Mapped[str] = mapped_column(
        String(255),
        default=generate_public_token,
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        default="",
        nullable=False,
    )

    status: Mapped[ProjectStatus] = mapped_column(
        SqlEnum(ProjectStatus, name="project_status"),
        default=ProjectStatus.ACTIVE,
        nullable=False,
        index=True,
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

    documents = relationship(
        "ProjectDoc",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    release_notes = relationship(
        "ReleaseNote",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    story_points = relationship(
        "StoryPoint",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    feedbacks = relationship(
        "Feedback",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    story_points = relationship(
        "StoryPoint",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )