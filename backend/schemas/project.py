"""
project.py

Файл содержит Pydantic-схемы для работы с проектами
и документацией проектов:
- создание и изменение проекта;
- получение данных проекта через API;
- фильтрацию проектов по статусу;
- создание, изменение и получение документов проекта.

Статусы проекта соответствуют модели Project:
- active — текущий проект;
- completed — завершённый проект;
- archived — архивный проект.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from models.project import ProjectStatus
from schemas.common import ORMBaseModel


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=10000)
    status: ProjectStatus = ProjectStatus.ACTIVE

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название проекта не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return value.strip()


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    status: ProjectStatus | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Название проекта не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip()


class ProjectRead(ORMBaseModel):
    id: int
    public_token: str
    name: str
    description: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectPublicRead(ORMBaseModel):
    id: int
    name: str
    description: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime


class ProjectFilter(BaseModel):
    status: ProjectStatus | None = None


class ProjectDocCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    content: str = Field(default="", max_length=50000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Заголовок документа не может быть пустым")

        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        return value.strip()


class ProjectDocUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    content: str | None = Field(default=None, max_length=50000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Заголовок документа не может быть пустым")

        return value

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip()


class ProjectDocRead(ORMBaseModel):
    id: int
    project_id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime