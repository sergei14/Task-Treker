"""
attachment.py

Модель вложений (файлов), которые могут быть прикреплены к:
- задачам;
- подзадачам;
- фидбекам;
- проектам (в будущем).

Почему это важно:
- один универсальный механизм хранения файлов;
- не нужно делать отдельные таблицы под каждый тип файлов;
- легко перейти на внешнее хранилище (S3 / MinIO).
"""

from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class Attachment(Base):
    """
    Таблица вложений.

    Хранит метаданные файлов, сами файлы лежат в файловой системе.
    """

    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    # =========================
    # Привязка к сущности
    # =========================
    # универсальный подход: можем привязать к любому объекту
    entity_type: Mapped[str] = mapped_column(String, index=True)
    entity_id: Mapped[int] = mapped_column(Integer, index=True)

    # =========================
    # Информация о файле
    # =========================
    filename: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)

    # MIME type (image/png, application/pdf и т.д.)
    content_type: Mapped[str] = mapped_column(String)

    # размер файла в байтах
    size: Mapped[int] = mapped_column(Integer)

    # =========================
    # Метаданные
    # =========================
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )