"""
tasks.py

Файл содержит API-маршруты для работы с задачами проекта:
- создание, просмотр, изменение и удаление задач;
- фильтрацию задач по статусу и приоритету;
- работу с подзадачами;
- работу со сторипоинтами;
- получение общей суммы сторипоинтов проекта.

Роутер подключается в main.py с общим префиксом /api.
Итоговые адреса будут начинаться с /api/projects/{project_id}/tasks.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from models.subtask import SubtaskStatus
from models.task import TaskPriority, TaskStatus
from schemas.common import MessageResponse, PaginationParams
from schemas.task import (
    StoryPointCreate,
    StoryPointRead,
    StoryPointUpdate,
    SubtaskCreate,
    SubtaskRead,
    SubtaskUpdate,
    TaskCreate,
    TaskDetailRead,
    TaskRead,
    TaskUpdate,
)
from services.task_service import (
    create_story_point,
    create_subtask,
    create_task,
    delete_story_point,
    delete_subtask,
    delete_task,
    get_project_story_points_total,
    get_project_task_detail_or_404,
    get_project_tasks,
    get_task_story_point_or_404,
    get_task_subtasks,
    update_story_point,
    update_subtask,
    update_task,
)


router = APIRouter(
    prefix="/projects/{project_id}/tasks",
    tags=["Tasks"],
)


@router.get(
    "",
    response_model=list[TaskRead],
)
def read_project_tasks(
    project_id: int,
    task_status: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = Query(default=None),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
) -> list[TaskRead]:
    return get_project_tasks(
        db=db,
        project_id=project_id,
        task_status=task_status,
        priority=priority,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.post(
    "",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
) -> TaskRead:
    return create_task(
        db=db,
        project_id=project_id,
        task_data=task_data,
    )


@router.get(
    "/story-points/total",
    response_model=int,
)
def read_project_story_points_total(
    project_id: int,
    db: Session = Depends(get_db),
) -> int:
    return get_project_story_points_total(
        db=db,
        project_id=project_id,
    )


@router.get(
    "/{task_id}",
    response_model=TaskDetailRead,
)
def read_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
) -> TaskDetailRead:
    return get_project_task_detail_or_404(
        db=db,
        project_id=project_id,
        task_id=task_id,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskRead,
)
def edit_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
) -> TaskRead:
    return update_task(
        db=db,
        project_id=project_id,
        task_id=task_id,
        task_data=task_data,
    )


@router.delete(
    "/{task_id}",
    response_model=MessageResponse,
)
def remove_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_task(
        db=db,
        project_id=project_id,
        task_id=task_id,
    )

    return MessageResponse(message="Задача успешно удалена")


@router.get(
    "/{task_id}/subtasks",
    response_model=list[SubtaskRead],
)
def read_task_subtasks(
    project_id: int,
    task_id: int,
    subtask_status: SubtaskStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[SubtaskRead]:
    return get_task_subtasks(
        db=db,
        project_id=project_id,
        task_id=task_id,
        subtask_status=subtask_status,
    )


@router.post(
    "/{task_id}/subtasks",
    response_model=SubtaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_new_subtask(
    project_id: int,
    task_id: int,
    subtask_data: SubtaskCreate,
    db: Session = Depends(get_db),
) -> SubtaskRead:
    return create_subtask(
        db=db,
        project_id=project_id,
        task_id=task_id,
        subtask_data=subtask_data,
    )


@router.patch(
    "/{task_id}/subtasks/{subtask_id}",
    response_model=SubtaskRead,
)
def edit_subtask(
    project_id: int,
    task_id: int,
    subtask_id: int,
    subtask_data: SubtaskUpdate,
    db: Session = Depends(get_db),
) -> SubtaskRead:
    return update_subtask(
        db=db,
        project_id=project_id,
        task_id=task_id,
        subtask_id=subtask_id,
        subtask_data=subtask_data,
    )


@router.delete(
    "/{task_id}/subtasks/{subtask_id}",
    response_model=MessageResponse,
)
def remove_subtask(
    project_id: int,
    task_id: int,
    subtask_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_subtask(
        db=db,
        project_id=project_id,
        task_id=task_id,
        subtask_id=subtask_id,
    )

    return MessageResponse(message="Подзадача успешно удалена")


@router.get(
    "/{task_id}/story-points",
    response_model=StoryPointRead,
)
def read_task_story_points(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
) -> StoryPointRead:
    return get_task_story_point_or_404(
        db=db,
        project_id=project_id,
        task_id=task_id,
    )


@router.post(
    "/{task_id}/story-points",
    response_model=StoryPointRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task_story_points(
    project_id: int,
    task_id: int,
    story_point_data: StoryPointCreate,
    db: Session = Depends(get_db),
) -> StoryPointRead:
    return create_story_point(
        db=db,
        project_id=project_id,
        task_id=task_id,
        story_point_data=story_point_data,
    )


@router.patch(
    "/{task_id}/story-points",
    response_model=StoryPointRead,
)
def edit_task_story_points(
    project_id: int,
    task_id: int,
    story_point_data: StoryPointUpdate,
    db: Session = Depends(get_db),
) -> StoryPointRead:
    return update_story_point(
        db=db,
        project_id=project_id,
        task_id=task_id,
        story_point_data=story_point_data,
    )


@router.delete(
    "/{task_id}/story-points",
    response_model=MessageResponse,
)
def remove_task_story_points(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
) -> MessageResponse:
    delete_story_point(
        db=db,
        project_id=project_id,
        task_id=task_id,
    )

    return MessageResponse(message="Оценка задачи успешно удалена")