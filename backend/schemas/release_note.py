"""
release_note.py

Файл содержит Pydantic-схемы для работы с релизнотами проекта:
- создание релизной заметки;
- изменение существующей релизной заметки;
- получение релизнота через API.

Релизноты относятся к конкретному проекту
и содержат версию, название и описание изменений.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from schemas.common import ORMBaseModel


class ReleaseNoteCreate(BaseModel):
    version: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=10000)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Версия релиза не может быть пустой")

        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название релиза не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return value.strip()


class ReleaseNoteUpdate(BaseModel):
    version: str | None = Field(default=None, min_length=1, max_length=50)
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)

    @field_validator("version")
    @classmethod
    def validate_version(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Версия релиза не может быть пустой")

        return value

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Название релиза не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip()


class ReleaseNoteRead(ORMBaseModel):
    id: int
    project_id: int
    version: str
    title: str
    description: str
    created_at: datetime
    updated_at: datetime