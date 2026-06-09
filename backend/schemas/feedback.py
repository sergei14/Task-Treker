"""
feedback.py

Файл содержит Pydantic-схемы для работы с обратной связью:
- создание комментария пользователем;
- редактирование фидбека;
- получение данных о фидбеке через API;
- фильтрацию фидбеков по типу.

Типы обратной связи соответствуют модели Feedback:
- bug — сообщение об ошибке;
- feature — пожелание или предложение;
- case — описание кейса использования.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from models.feedback import FeedbackType
from schemas.common import ORMBaseModel


class FeedbackCreate(BaseModel):
    type: FeedbackType
    full_name: str | None = Field(default=None, max_length=150)
    direction: str | None = Field(default=None, max_length=150)
    comment: str = Field(min_length=1, max_length=5000)

    @field_validator("full_name", "direction")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Комментарий не может быть пустым")

        return value


class FeedbackUpdate(BaseModel):
    type: FeedbackType | None = None
    full_name: str | None = Field(default=None, max_length=150)
    direction: str | None = Field(default=None, max_length=150)
    comment: str | None = Field(default=None, min_length=1, max_length=5000)

    @field_validator("full_name", "direction")
    @classmethod
    def validate_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()
        return value or None

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Комментарий не может быть пустым")

        return value


class FeedbackRead(ORMBaseModel):
    id: int
    project_id: int
    type: FeedbackType
    full_name: str | None
    direction: str | None
    comment: str
    created_at: datetime


class FeedbackFilter(BaseModel):
    type: FeedbackType | None = None