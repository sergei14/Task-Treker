"""
story_point.py

Модель оценки задачи в сторипоинтах.

Сторипоинты используются для оценки объёма или сложности работы.
Оценка относится к конкретной задаче внутри проекта.

У одной задачи может быть только одна актуальная оценка.
Общую оценку проекта можно будет получить как сумму
сторипоинтов всех его задач.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class StoryPoint(Base):
    __tablename__ = "story_points"
    __table_args__ = (
        UniqueConstraint(
            "task_id",
            name="uq_story_point_task_id",
        ),
        CheckConstraint(
            "points >= 0",
            name="ck_story_points_non_negative",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    points: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
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
        back_populates="story_points",
    )

    task = relationship(
        "Task",
        back_populates="story_point",
    )