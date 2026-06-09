"""
file_upload.py

Файл содержит вспомогательные функции для работы с вложениями:
- проверяет имя, расширение и размер загружаемого файла;
- сохраняет файл в папку backend/uploads;
- создаёт уникальное имя файла на сервере;
- возвращает данные для записи в модель Attachment;
- удаляет сохранённый файл при необходимости.

В базе данных хранится относительный путь к файлу,
а само содержимое файла находится в файловой системе.
"""

from pathlib import Path
from typing import TypedDict
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings


CHUNK_SIZE = 1024 * 1024


class UploadedFileData(TypedDict):
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    size: int


def get_safe_filename(filename: str) -> str:
    safe_filename = Path(filename).name.strip()

    if not safe_filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Имя файла не указано",
        )

    return safe_filename


def validate_file_extension(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    if extension not in settings.allowed_file_extensions:
        allowed_extensions = ", ".join(settings.allowed_file_extensions)

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый формат файла. Разрешены: {allowed_extensions}",
        )

    return extension


def save_upload_file(upload_file: UploadFile) -> UploadedFileData:
    if upload_file.filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Файл не выбран",
        )

    original_filename = get_safe_filename(upload_file.filename)
    extension = validate_file_extension(original_filename)

    stored_filename = f"{uuid4().hex}{extension}"
    uploads_path = settings.get_upload_path()
    saved_file_path = uploads_path / stored_filename

    file_size = 0

    try:
        upload_file.file.seek(0)

        with saved_file_path.open("wb") as destination:
            while True:
                chunk = upload_file.file.read(CHUNK_SIZE)

                if not chunk:
                    break

                file_size += len(chunk)

                if file_size > settings.max_upload_bytes:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            f"Размер файла превышает допустимый лимит "
                            f"{settings.max_upload_mb} МБ"
                        ),
                    )

                destination.write(chunk)

    except HTTPException:
        if saved_file_path.exists():
            saved_file_path.unlink()

        raise

    except OSError as error:
        if saved_file_path.exists():
            saved_file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось сохранить файл",
        ) from error

    finally:
        upload_file.file.close()

    if file_size == 0:
        if saved_file_path.exists():
            saved_file_path.unlink()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя загрузить пустой файл",
        )

    relative_file_path = str(settings.uploads_dir / stored_filename)

    return UploadedFileData(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=relative_file_path,
        content_type=upload_file.content_type or "application/octet-stream",
        size=file_size,
    )


def delete_upload_file(file_path: str) -> None:
    uploads_path = settings.get_upload_path().resolve()
    saved_file_path = (settings.base_dir / file_path).resolve()

    if uploads_path not in saved_file_path.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Некорректный путь к файлу",
        )

    if not saved_file_path.exists():
        return

    try:
        saved_file_path.unlink()
    except OSError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить файл",
        ) from error