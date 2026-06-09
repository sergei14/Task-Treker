"""
config.py

Файл хранит основные настройки backend-приложения:
- название, версию и режим запуска;
- настройки базы данных;
- пути к папкам загрузок и логов;
- настройки API и CORS;
- ограничения для файлов;
- параметры публичных токенов;
- настройки логирования.

Значения можно переопределять через переменные окружения
или файл backend/.env.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_PATH = BACKEND_DIR / "tracker.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"


class Settings(BaseSettings):
    app_name: str = "Task Tracker API"
    app_version: str = "0.1.0"
    debug: bool = True
    environment: Literal["development", "testing", "production"] = "development"

    api_prefix: str = "/api"

    database_url: str = DEFAULT_DATABASE_URL

    base_dir: Path = BACKEND_DIR
    uploads_dir: Path = Path("uploads")
    logs_dir: Path = Path("logs")

    cors_origins: list[str] = ["*"]

    max_upload_mb: int = 2

    allowed_file_extensions: list[str] = [
        ".png",
        ".jpg",
        ".jpeg",
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
    ]

    token_length: int = 32

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("api_prefix")
    @classmethod
    def validate_api_prefix(cls, value: str) -> str:
        value = value.strip()

        if not value:
            return "/api"

        if not value.startswith("/"):
            value = f"/{value}"

        return value.rstrip("/")

    @field_validator("max_upload_mb")
    @classmethod
    def validate_max_upload_mb(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("max_upload_mb должен быть больше нуля")

        return value

    @field_validator("token_length")
    @classmethod
    def validate_token_length(cls, value: int) -> int:
        if value < 16:
            raise ValueError("token_length должен быть не меньше 16")

        return value

    @property
    def max_upload_bytes(self) -> int:
        return self.max_upload_mb * 1024 * 1024

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    def get_upload_path(self) -> Path:
        upload_path = self.base_dir / self.uploads_dir
        upload_path.mkdir(parents=True, exist_ok=True)
        return upload_path

    def get_logs_path(self) -> Path:
        logs_path = self.base_dir / self.logs_dir
        logs_path.mkdir(parents=True, exist_ok=True)
        return logs_path


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()