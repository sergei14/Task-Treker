"""
files.py

Файл содержит API-маршруты для работы с вложениями:
- загрузку файла для объекта трекера;
- получение списка вложений объекта;
- скачивание сохранённого файла;
- удаление вложения.

Файлы можно прикреплять к:
- проектам;
- документации;
- релизнотам;
- задачам;
- подзадачам;
- фидбекам.

Сам файл сохраняется в папке backend/uploads,
а его данные хранятся в таблице attachments.
"""

from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from models.attachment import Attachment
from models.feedback import Feedback
from models.project import Project
from models.project_doc import ProjectDoc
from models.release_note import ReleaseNote
from models.subtask import Subtask
from models.task import Task
from schemas.common import MessageResponse, ORMBaseModel
from utils.file_upload import delete_upload_file, save_upload_file


EntityType = Literal[
    "project",
    "project_doc",
    "release_note",
    "task",
    "subtask",
    "feedback",
]


class AttachmentRead(ORMBaseModel):
    id: int
    entity_type: str
    entity_id: int
    original_filename: str
    stored_filename: str
    file_path: str
    content_type: str
    size: int
    created_at: datetime


ENTITY_MODELS = {
    "project": Project,
    "project_doc": ProjectDoc,
    "release_note": ReleaseNote,
    "task": Task,
    "subtask": Subtask,
    "feedback": Feedback,
}


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


def get_entity_or_404(
    db: Session,
    entity_type: EntityType,
    entity_id: int,
) -> None:
    model = ENTITY_MODELS[entity_type]

    entity = db.scalar(
        select(model).where(model.id == entity_id)
    )

    if entity is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Объект для прикрепления файла не найден",
        )


def get_attachment_or_404(
    db: Session,
    attachment_id: int,
) -> Attachment:
    attachment = db.scalar(
        select(Attachment).where(Attachment.id == attachment_id)
    )

    if attachment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вложение не найдено",
        )

    return attachment


def get_attachment_path_or_404(attachment: Attachment) -> Path:
    uploads_path = settings.get_upload_path().resolve()
    attachment_path = (settings.base_dir / attachment.file_path).resolve()

    if uploads_path not in attachment_path.parents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден",
        )

    if not attachment_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Файл не найден",
        )

    return attachment_path


@router.get(
    "/{attachment_id}/download",
)
def download_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
) -> FileResponse:
    attachment = get_attachment_or_404(
        db=db,
        attachment_id=attachment_id,
    )

    attachment_path = get_attachment_path_or_404(attachment)

    return FileResponse(
        path=attachment_path,
        media_type=attachment.content_type,
        filename=attachment.original_filename,
    )


@router.delete(
    "/{attachment_id}",
    response_model=MessageResponse,
)
def remove_attachment(
    attachment_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    attachment = get_attachment_or_404(
        db=db,
        attachment_id=attachment_id,
    )

    delete_upload_file(attachment.file_path)
    db.delete(attachment)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return MessageResponse(message="Вложение успешно удалено")


@router.get(
    "/{entity_type}/{entity_id}",
    response_model=list[AttachmentRead],
)
def read_entity_attachments(
    entity_type: EntityType,
    entity_id: int,
    db: Session = Depends(get_db),
) -> list[AttachmentRead]:
    get_entity_or_404(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    statement = (
        select(Attachment)
        .where(
            Attachment.entity_type == entity_type,
            Attachment.entity_id == entity_id,
        )
        .order_by(Attachment.created_at.desc())
    )

    return list(db.scalars(statement).all())


@router.post(
    "/{entity_type}/{entity_id}",
    response_model=AttachmentRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_entity_attachment(
    entity_type: EntityType,
    entity_id: int,
    file: UploadFile,
    db: Session = Depends(get_db),
) -> AttachmentRead:
    get_entity_or_404(
        db=db,
        entity_type=entity_type,
        entity_id=entity_id,
    )

    file_data = save_upload_file(file)

    attachment = Attachment(
        entity_type=entity_type,
        entity_id=entity_id,
        **file_data,
    )

    db.add(attachment)

    try:
        db.commit()
        db.refresh(attachment)
    except Exception:
        db.rollback()

        try:
            delete_upload_file(file_data["file_path"])
        except HTTPException:
            pass

        raise

    return attachment