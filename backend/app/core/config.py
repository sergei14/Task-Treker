"""
config.py

Этот файл хранит все настройки приложения в одном месте.

Здесь определяются:
- основные параметры приложения (имя, версия, режим);
- настройки базы данных;
- пути к файлам;
- настройки API;
- лимиты и служебные параметры.

Все значения можно переопределять через:
- переменные окружения
- файл .env
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Основной класс настроек приложения.

    Pydantic автоматически:
    - читает значения из .env
    - читает переменные окружения
    - валидирует типы

    Приоритет значений:
    1. Переменные окружения
    2. .env файл
    3. Значения по умолчанию
    """

    # =========================
    # Общие настройки
    # =========================
    app_name: str = "Task Tracker"
    app_version: str = "0.1.0"
    debug: bool = True

    # Окружение: development / staging / production
    environment: str = Field(default="development")

    # =========================
    # База данных
    # =========================
    # Для разработки используем SQLite.
    # В будущем можно заменить на Postgres без изменения кода.
    database_url: str = "sqlite+aiosqlite:///./tracker.db"

    # =========================
    # Пути
    # =========================
    # Корень проекта (tracker/)
    base_dir: Path = Path(__file__).resolve().parents[3]

    # Относительный путь для загрузки файлов
    uploads_dir: Path = Path("uploads")

    # =========================
    # API
    # =========================
    api_prefix: str = "/api"

    # =========================
    # CORS (⚠️ только для разработки)
    # =========================
    cors_origins: List[str] = ["*"]

    # =========================
    # Файлы
    # =========================
    max_upload_mb: int = 2

    # =========================
    # Токены (для публичного фидбека)
    # =========================
    token_length: int = 32

    # =========================
    # Логирование
    # =========================
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def get_upload_path(self) -> Path:
        """
        Возвращает абсолютный путь к папке uploads
        и создаёт её при необходимости.

        Returns:
            Path: полный путь до директории загрузок
        """
        full_path = self.base_dir / self.uploads_dir
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path


@lru_cache
def get_settings() -> Settings:
    """
    Возвращает singleton-объект настроек.

    Используем кэш, чтобы:
    - не перечитывать .env при каждом импорте
    - использовать один объект во всём приложении
    """
    return Settings()


# Глобальный объект настроек
settings = get_settings()