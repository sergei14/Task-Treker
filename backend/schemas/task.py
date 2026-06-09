"""
task.py

Файл содержит Pydantic-схемы для работы с задачами проекта:
- создание и изменение задач;
- создание и изменение подзадач;
- установка оценки задачи в сторипоинтах;
- получение данных о задачах через API;
- фильтрацию задач по статусу и приоритету.

Задача относится к конкретному проекту.
Подзадача относится к конкретной задаче.
У одной задачи может быть одна актуальная оценка в сторипоинтах.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from models.subtask import SubtaskStatus
from models.task import TaskPriority, TaskStatus
from schemas.common import ORMBaseModel


class StoryPointCreate(BaseModel):
    points: int = Field(default=0, ge=0)


class StoryPointUpdate(BaseModel):
    points: int = Field(ge=0)


class StoryPointRead(ORMBaseModel):
    id: int
    project_id: int
    task_id: int
    points: int
    created_at: datetime
    updated_at: datetime


class SubtaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=10000)
    status: SubtaskStatus = SubtaskStatus.TODO
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название подзадачи не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return value.strip()


class SubtaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    status: SubtaskStatus | None = None
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Название подзадачи не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip()


class SubtaskRead(ORMBaseModel):
    id: int
    task_id: int
    title: str
    description: str
    status: SubtaskStatus
    deadline: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(default="", max_length=10000)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    deadline: datetime | None = None
    story_points: int | None = Field(default=None, ge=0)

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Название задачи не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        return value.strip()


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=10000)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    deadline: datetime | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Название задачи не может быть пустым")

        return value

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None

        return value.strip()


class TaskRead(ORMBaseModel):
    id: int
    project_id: int
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    deadline: datetime | None
    created_at: datetime
    updated_at: datetime


class TaskDetailRead(TaskRead):
    subtasks: list[SubtaskRead]
    story_point: StoryPointRead | None


class TaskFilter(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None