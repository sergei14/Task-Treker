"""
common.py

Файл содержит общие Pydantic-схемы, которые используются
в разных разделах API:
- базовую схему для преобразования ORM-моделей в JSON;
- стандартный ответ с сообщением;
- параметры пагинации для списков проектов, задач и фидбеков.

Остальные схемы проекта будут наследоваться от ORMBaseModel,
чтобы FastAPI мог возвращать данные из SQLAlchemy-моделей.
"""

from pydantic import BaseModel, ConfigDict, Field


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str


class PaginationParams(BaseModel):
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)