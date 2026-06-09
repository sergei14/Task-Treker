"""
project_service.py

Файл содержит бизнес-логику для работы с проектами:
- создание, получение, изменение и удаление проектов;
- получение проекта по публичному токену;
- фильтрацию проектов по статусу;
- работу с документацией проекта;
- работу с релизнотами проекта.

Документация и релизноты всегда создаются
только внутри существующего проекта.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.project import Project, ProjectStatus
from models.project_doc import ProjectDoc
from models.release_note import ReleaseNote
from schemas.project import (
    ProjectCreate,
    ProjectDocCreate,
    ProjectDocUpdate,
    ProjectUpdate,
)
from schemas.release_note import ReleaseNoteCreate, ReleaseNoteUpdate


def get_project_or_404(db: Session, project_id: int) -> Project:
    project = db.scalar(
        select(Project).where(Project.id == project_id)
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    return project


def get_project_by_token_or_404(db: Session, public_token: str) -> Project:
    project = db.scalar(
        select(Project).where(Project.public_token == public_token)
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    return project


def get_projects(
    db: Session,
    project_status: ProjectStatus | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Project]:
    statement = select(Project)

    if project_status is not None:
        statement = statement.where(Project.status == project_status)

    statement = (
        statement
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_project(
    db: Session,
    project_data: ProjectCreate,
) -> Project:
    project = Project(**project_data.model_dump())

    db.add(project)

    try:
        db.commit()
        db.refresh(project)
    except Exception:
        db.rollback()
        raise

    return project


def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate,
) -> Project:
    project = get_project_or_404(db, project_id)
    update_data = project_data.model_dump(exclude_unset=True)

    required_fields = {"name", "description", "status"}

    for field, value in update_data.items():
        if field in required_fields and value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Поле '{field}' не может быть пустым",
            )

        setattr(project, field, value)

    try:
        db.commit()
        db.refresh(project)
    except Exception:
        db.rollback()
        raise

    return project


def delete_project(
    db: Session,
    project_id: int,
) -> None:
    project = get_project_or_404(db, project_id)

    db.delete(project)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_project_document_or_404(
    db: Session,
    project_id: int,
    document_id: int,
) -> ProjectDoc:
    get_project_or_404(db, project_id)

    document = db.scalar(
        select(ProjectDoc).where(
            ProjectDoc.id == document_id,
            ProjectDoc.project_id == project_id,
        )
    )

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ проекта не найден",
        )

    return document


def get_project_documents(
    db: Session,
    project_id: int,
) -> list[ProjectDoc]:
    get_project_or_404(db, project_id)

    statement = (
        select(ProjectDoc)
        .where(ProjectDoc.project_id == project_id)
        .order_by(ProjectDoc.created_at.desc())
    )

    return list(db.scalars(statement).all())


def create_project_document(
    db: Session,
    project_id: int,
    document_data: ProjectDocCreate,
) -> ProjectDoc:
    project = get_project_or_404(db, project_id)

    document = ProjectDoc(
        project_id=project.id,
        **document_data.model_dump(),
    )

    db.add(document)

    try:
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

    return document


def update_project_document(
    db: Session,
    project_id: int,
    document_id: int,
    document_data: ProjectDocUpdate,
) -> ProjectDoc:
    document = get_project_document_or_404(db, project_id, document_id)
    update_data = document_data.model_dump(exclude_unset=True)

    required_fields = {"title", "content"}

    for field, value in update_data.items():
        if field in required_fields and value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Поле '{field}' не может быть пустым",
            )

        setattr(document, field, value)

    try:
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

    return document


def delete_project_document(
    db: Session,
    project_id: int,
    document_id: int,
) -> None:
    document = get_project_document_or_404(db, project_id, document_id)

    db.delete(document)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_release_note_or_404(
    db: Session,
    project_id: int,
    release_note_id: int,
) -> ReleaseNote:
    get_project_or_404(db, project_id)

    release_note = db.scalar(
        select(ReleaseNote).where(
            ReleaseNote.id == release_note_id,
            ReleaseNote.project_id == project_id,
        )
    )

    if release_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Релизнот проекта не найден",
        )

    return release_note


def get_project_release_notes(
    db: Session,
    project_id: int,
) -> list[ReleaseNote]:
    get_project_or_404(db, project_id)

    statement = (
        select(ReleaseNote)
        .where(ReleaseNote.project_id == project_id)
        .order_by(ReleaseNote.created_at.desc())
    )

    return list(db.scalars(statement).all())


def create_release_note(
    db: Session,
    project_id: int,
    release_note_data: ReleaseNoteCreate,
) -> ReleaseNote:
    project = get_project_or_404(db, project_id)

    existing_release_note = db.scalar(
        select(ReleaseNote).where(
            ReleaseNote.project_id == project_id,
            ReleaseNote.version == release_note_data.version,
        )
    )

    if existing_release_note is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Релизнот с такой версией уже существует в проекте",
        )

    release_note = ReleaseNote(
        project_id=project.id,
        **release_note_data.model_dump(),
    )

    db.add(release_note)

    try:
        db.commit()
        db.refresh(release_note)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Релизнот с такой версией уже существует в проекте",
        )
    except Exception:
        db.rollback()
        raise

    return release_note


def update_release_note(
    db: Session,
    project_id: int,
    release_note_id: int,
    release_note_data: ReleaseNoteUpdate,
) -> ReleaseNote:
    release_note = get_release_note_or_404(db, project_id, release_note_id)
    update_data = release_note_data.model_dump(exclude_unset=True)

    required_fields = {"version", "title", "description"}

    for field, value in update_data.items():
        if field in required_fields and value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Поле '{field}' не может быть пустым",
            )

    new_version = update_data.get("version")

    if new_version is not None and new_version != release_note.version:
        existing_release_note = db.scalar(
            select(ReleaseNote).where(
                ReleaseNote.project_id == project_id,
                ReleaseNote.version == new_version,
                ReleaseNote.id != release_note_id,
            )
        )

        if existing_release_note is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Релизнот с такой версией уже существует в проекте",
            )

    for field, value in update_data.items():
        setattr(release_note, field, value)

    try:
        db.commit()
        db.refresh(release_note)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Релизнот с такой версией уже существует в проекте",
        )
    except Exception:
        db.rollback()
        raise

    return release_note


def delete_release_note(
    db: Session,
    project_id: int,
    release_note_id: int,
) -> None:
    release_note = get_release_note_or_404(db, project_id, release_note_id)

    db.delete(release_note)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise