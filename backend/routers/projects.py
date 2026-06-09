"""
projects.py

Файл содержит API-маршруты для работы с проектами:
- создание, просмотр, изменение и удаление проектов;
- получение проекта по публичному токену;
- работу с документацией проекта;
- работу с релизнотами проекта.

Роутер подключается в main.py с общим префиксом /api.
Итоговые адреса будут начинаться с /api/projects.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from models.project import ProjectStatus
from schemas.common import MessageResponse, PaginationParams
from schemas.project import (
    ProjectCreate,
    ProjectDocCreate,
    ProjectDocRead,
    ProjectDocUpdate,
    ProjectPublicRead,
    ProjectRead,
    ProjectUpdate,
)
from schemas.release_note import (
    ReleaseNoteCreate,
    ReleaseNoteRead,
    ReleaseNoteUpdate,
)
from services.project_service import (
    create_project,
    create_project_document,
    create_release_note,
    delete_project,
    delete_project_document,
    delete_release_note,
    get_project_by_token_or_404,
    get_project_document_or_404,
    get_project_documents,
    get_project_or_404,
    get_project_release_notes,
    get_projects,
    get_release_note_or_404,
    update_project,
    update_project_document,
    update_release_note,
)
from utils.token_parser import is_valid_public_token, normalize_public_token


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.get(
    "",
    response_model=list[ProjectRead],
)
def read_projects(
    project_status: ProjectStatus | None = Query(default=None, alias="status"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
) -> list[ProjectRead]:
    return get_projects(
        db=db,
        project_status=project_status,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
) -> ProjectRead:
    return create_project(
        db=db,
        project_data=project_data,
    )


@router.get(
    "/public/{public_token}",
    response_model=ProjectPublicRead,
)
def read_public_project(
    public_token: str,
    db: Session = Depends(get_db),
) -> ProjectPublicRead:
    public_token = normalize_public_token(public_token)

    if not is_valid_public_token(public_token):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    return get_project_by_token_or_404(
        db=db,
        public_token=public_token,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectRead,
)
def read_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> ProjectRead:
    return get_project_or_404(
        db=db,
        project_id=project_id,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectRead,
)
def edit_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
) -> ProjectRead:
    return update_project(
        db=db,
        project_id=project_id,
        project_data=project_data,
    )


@router.delete(
    "/{project_id}",
    response_model=MessageResponse,
)
def remove_project(
    project_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_project(
        db=db,
        project_id=project_id,
    )

    return MessageResponse(message="Проект успешно удалён")


@router.get(
    "/{project_id}/documents",
    response_model=list[ProjectDocRead],
)
def read_project_documents(
    project_id: int,
    db: Session = Depends(get_db),
) -> list[ProjectDocRead]:
    return get_project_documents(
        db=db,
        project_id=project_id,
    )


@router.post(
    "/{project_id}/documents",
    response_model=ProjectDocRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_project_document(
    project_id: int,
    document_data: ProjectDocCreate,
    db: Session = Depends(get_db),
) -> ProjectDocRead:
    return create_project_document(
        db=db,
        project_id=project_id,
        document_data=document_data,
    )


@router.get(
    "/{project_id}/documents/{document_id}",
    response_model=ProjectDocRead,
)
def read_project_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
) -> ProjectDocRead:
    return get_project_document_or_404(
        db=db,
        project_id=project_id,
        document_id=document_id,
    )


@router.patch(
    "/{project_id}/documents/{document_id}",
    response_model=ProjectDocRead,
)
def edit_project_document(
    project_id: int,
    document_id: int,
    document_data: ProjectDocUpdate,
    db: Session = Depends(get_db),
) -> ProjectDocRead:
    return update_project_document(
        db=db,
        project_id=project_id,
        document_id=document_id,
        document_data=document_data,
    )


@router.delete(
    "/{project_id}/documents/{document_id}",
    response_model=MessageResponse,
)
def remove_project_document(
    project_id: int,
    document_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_project_document(
        db=db,
        project_id=project_id,
        document_id=document_id,
    )

    return MessageResponse(message="Документ проекта успешно удалён")


@router.get(
    "/{project_id}/release-notes",
    response_model=list[ReleaseNoteRead],
)
def read_project_release_notes(
    project_id: int,
    db: Session = Depends(get_db),
) -> list[ReleaseNoteRead]:
    return get_project_release_notes(
        db=db,
        project_id=project_id,
    )


@router.post(
    "/{project_id}/release-notes",
    response_model=ReleaseNoteRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_release_note(
    project_id: int,
    release_note_data: ReleaseNoteCreate,
    db: Session = Depends(get_db),
) -> ReleaseNoteRead:
    return create_release_note(
        db=db,
        project_id=project_id,
        release_note_data=release_note_data,
    )


@router.get(
    "/{project_id}/release-notes/{release_note_id}",
    response_model=ReleaseNoteRead,
)
def read_release_note(
    project_id: int,
    release_note_id: int,
    db: Session = Depends(get_db),
) -> ReleaseNoteRead:
    return get_release_note_or_404(
        db=db,
        project_id=project_id,
        release_note_id=release_note_id,
    )


@router.patch(
    "/{project_id}/release-notes/{release_note_id}",
    response_model=ReleaseNoteRead,
)
def edit_release_note(
    project_id: int,
    release_note_id: int,
    release_note_data: ReleaseNoteUpdate,
    db: Session = Depends(get_db),
) -> ReleaseNoteRead:
    return update_release_note(
        db=db,
        project_id=project_id,
        release_note_id=release_note_id,
        release_note_data=release_note_data,
    )


@router.delete(
    "/{project_id}/release-notes/{release_note_id}",
    response_model=MessageResponse,
)
def remove_release_note(
    project_id: int,
    release_note_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_release_note(
        db=db,
        project_id=project_id,
        release_note_id=release_note_id,
    )

    return MessageResponse(message="Релизнот успешно удалён")