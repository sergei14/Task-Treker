"""
feedback.py

Модель обратной связи по проекту.

Фидбек относится к конкретному проекту и представляет собой
комментарий одного из трёх типов:
- bug — сообщение об ошибке;
- feature — пожелание или предложение;
- case — описание кейса использования.

Фидбек может быть оставлен пользователем через публичную страницу
проекта без обязательной авторизации(пока что).
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FeedbackType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    CASE = "case"


class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    type: Mapped[FeedbackType] = mapped_column(
        SqlEnum(FeedbackType, name="feedback_type"),
        nullable=False,
        index=True,
    )

    full_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    direction: Mapped[str | None] = mapped_column(String(150), nullable=True)

    comment: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    project = relationship("Project", back_populates="feedbacks")