"""
feedbacks.py

Файл содержит API-маршруты для работы с обратной связью:
- получение фидбеков конкретного проекта;
- создание фидбека внутри проекта;
- публичную отправку фидбека по токену проекта;
- изменение и удаление фидбека;
- фильтрацию фидбеков по типу.

Поддерживаются три типа обратной связи:
- bug — сообщение об ошибке;
- feature — пожелание или предложение;
- case — описание кейса использования.

Роутер подключается в main.py с общим префиксом /api.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from models.feedback import FeedbackType
from schemas.common import MessageResponse, PaginationParams
from schemas.feedback import FeedbackCreate, FeedbackRead, FeedbackUpdate
from services.feedback_service import (
    create_feedback,
    create_feedback_by_public_token,
    delete_feedback,
    get_feedback_or_404,
    get_project_feedbacks,
    update_feedback,
)
from utils.token_parser import is_valid_public_token, normalize_public_token


router = APIRouter(
    tags=["Feedbacks"],
)


@router.post(
    "/projects/public/{public_token}/feedbacks",
    response_model=FeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
def create_public_feedback(
    public_token: str,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    public_token = normalize_public_token(public_token)

    if not is_valid_public_token(public_token):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден",
        )

    return create_feedback_by_public_token(
        db=db,
        public_token=public_token,
        feedback_data=feedback_data,
    )


@router.get(
    "/projects/{project_id}/feedbacks",
    response_model=list[FeedbackRead],
)
def read_project_feedbacks(
    project_id: int,
    feedback_type: FeedbackType | None = Query(default=None, alias="type"),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
) -> list[FeedbackRead]:
    return get_project_feedbacks(
        db=db,
        project_id=project_id,
        feedback_type=feedback_type,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "/projects/{project_id}/feedbacks",
    response_model=FeedbackRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_feedback(
    project_id: int,
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    return create_feedback(
        db=db,
        project_id=project_id,
        feedback_data=feedback_data,
    )


@router.get(
    "/feedbacks/{feedback_id}",
    response_model=FeedbackRead,
)
def read_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    return get_feedback_or_404(
        db=db,
        feedback_id=feedback_id,
    )


@router.patch(
    "/feedbacks/{feedback_id}",
    response_model=FeedbackRead,
)
def edit_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    db: Session = Depends(get_db),
) -> FeedbackRead:
    return update_feedback(
        db=db,
        feedback_id=feedback_id,
        feedback_data=feedback_data,
    )


@router.delete(
    "/feedbacks/{feedback_id}",
    response_model=MessageResponse,
)
def remove_feedback(
    feedback_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_feedback(
        db=db,
        feedback_id=feedback_id,
    )

    return MessageResponse(message="Фидбек успешно удалён")