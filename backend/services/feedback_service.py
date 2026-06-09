"""
feedback_service.py

Файл содержит бизнес-логику для работы с обратной связью:
- создание фидбека внутри проекта;
- создание фидбека через публичный токен проекта;
- получение списка фидбеков проекта;
- фильтрацию по типу: bug, feature, case;
- изменение и удаление фидбека.

Фидбек всегда связан с существующим проектом.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.feedback import Feedback, FeedbackType
from models.project import Project
from schemas.feedback import FeedbackCreate, FeedbackUpdate


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


def get_feedback_or_404(db: Session, feedback_id: int) -> Feedback:
    feedback = db.scalar(
        select(Feedback).where(Feedback.id == feedback_id)
    )

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фидбек не найден",
        )

    return feedback


def get_project_feedback_or_404(
    db: Session,
    project_id: int,
    feedback_id: int,
) -> Feedback:
    get_project_or_404(db, project_id)

    feedback = db.scalar(
        select(Feedback).where(
            Feedback.id == feedback_id,
            Feedback.project_id == project_id,
        )
    )

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Фидбек не найден в данном проекте",
        )

    return feedback


def save_feedback(db: Session, feedback: Feedback) -> Feedback:
    db.add(feedback)

    try:
        db.commit()
        db.refresh(feedback)
    except Exception:
        db.rollback()
        raise

    return feedback


def create_feedback(
    db: Session,
    project_id: int,
    feedback_data: FeedbackCreate,
) -> Feedback:
    project = get_project_or_404(db, project_id)

    feedback = Feedback(
        project_id=project.id,
        **feedback_data.model_dump(),
    )

    return save_feedback(db, feedback)


def create_feedback_by_public_token(
    db: Session,
    public_token: str,
    feedback_data: FeedbackCreate,
) -> Feedback:
    project = get_project_by_token_or_404(db, public_token)

    feedback = Feedback(
        project_id=project.id,
        **feedback_data.model_dump(),
    )

    return save_feedback(db, feedback)


def get_project_feedbacks(
    db: Session,
    project_id: int,
    feedback_type: FeedbackType | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Feedback]:
    get_project_or_404(db, project_id)

    statement = select(Feedback).where(Feedback.project_id == project_id)

    if feedback_type is not None:
        statement = statement.where(Feedback.type == feedback_type)

    statement = (
        statement
        .order_by(Feedback.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def update_feedback(
    db: Session,
    feedback_id: int,
    feedback_data: FeedbackUpdate,
) -> Feedback:
    feedback = get_feedback_or_404(db, feedback_id)
    update_data = feedback_data.model_dump(exclude_unset=True)

    if "type" in update_data and update_data["type"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Тип фидбека не может быть пустым",
        )

    if "comment" in update_data and update_data["comment"] is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Комментарий не может быть пустым",
        )

    for field, value in update_data.items():
        setattr(feedback, field, value)

    return save_feedback(db, feedback)


def delete_feedback(db: Session, feedback_id: int) -> None:
    feedback = get_feedback_or_404(db, feedback_id)

    db.delete(feedback)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise