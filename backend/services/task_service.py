"""
task_service.py

Файл содержит бизнес-логику для работы с задачами проекта:
- создание, получение, изменение и удаление задач;
- фильтрацию задач по статусу и приоритету;
- работу с подзадачами;
- работу со сторипоинтами;
- подсчёт общей оценки задач проекта.

Задачи всегда принадлежат конкретному проекту.
Подзадачи и сторипоинты создаются только внутри существующей задачи.
"""
from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from models.project import Project
from models.story_point import StoryPoint
from models.subtask import Subtask, SubtaskStatus
from models.task import Task, TaskPriority, TaskStatus
from schemas.task import (
    StoryPointCreate,
    StoryPointUpdate,
    SubtaskCreate,
    SubtaskUpdate,
    TaskCreate,
    TaskUpdate,
)


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


def get_project_task_or_404(
    db: Session,
    project_id: int,
    task_id: int,
) -> Task:
    get_project_or_404(db, project_id)

    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.project_id == project_id,
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена в данном проекте",
        )

    return task


def get_project_task_detail_or_404(
    db: Session,
    project_id: int,
    task_id: int,
) -> Task:
    get_project_or_404(db, project_id)

    task = db.scalar(
        select(Task)
        .options(
            selectinload(Task.subtasks),
            selectinload(Task.story_point),
        )
        .where(
            Task.id == task_id,
            Task.project_id == project_id,
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Задача не найдена в данном проекте",
        )

    return task


def get_project_tasks(
    db: Session,
    project_id: int,
    task_status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Task]:
    get_project_or_404(db, project_id)

    statement = select(Task).where(Task.project_id == project_id)

    if task_status is not None:
        statement = statement.where(Task.status == task_status)

    if priority is not None:
        statement = statement.where(Task.priority == priority)

    statement = (
        statement
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    return list(db.scalars(statement).all())


def create_task(
    db: Session,
    project_id: int,
    task_data: TaskCreate,
) -> Task:
    project = get_project_or_404(db, project_id)

    task_values = task_data.model_dump(exclude={"story_points"})

    task = Task(
        project_id=project.id,
        **task_values,
    )

    db.add(task)

    try:
        db.flush()

        if task_data.story_points is not None:
            story_point = StoryPoint(
                project_id=project.id,
                task_id=task.id,
                points=task_data.story_points,
            )
            db.add(story_point)

        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise

    return task


def update_task(
    db: Session,
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
) -> Task:
    task = get_project_task_or_404(db, project_id, task_id)
    update_data = task_data.model_dump(exclude_unset=True)

    required_fields = {"title", "description", "status", "priority"}

    for field, value in update_data.items():
        if field in required_fields and value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Поле '{field}' не может быть пустым",
            )

        setattr(task, field, value)

    try:
        db.commit()
        db.refresh(task)
    except Exception:
        db.rollback()
        raise

    return task


def delete_task(
    db: Session,
    project_id: int,
    task_id: int,
) -> None:
    task = get_project_task_or_404(db, project_id, task_id)

    db.delete(task)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_task_subtask_or_404(
    db: Session,
    project_id: int,
    task_id: int,
    subtask_id: int,
) -> Subtask:
    get_project_task_or_404(db, project_id, task_id)

    subtask = db.scalar(
        select(Subtask).where(
            Subtask.id == subtask_id,
            Subtask.task_id == task_id,
        )
    )

    if subtask is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подзадача не найдена",
        )

    return subtask


def get_task_subtasks(
    db: Session,
    project_id: int,
    task_id: int,
    subtask_status: SubtaskStatus | None = None,
) -> list[Subtask]:
    get_project_task_or_404(db, project_id, task_id)

    statement = select(Subtask).where(Subtask.task_id == task_id)

    if subtask_status is not None:
        statement = statement.where(Subtask.status == subtask_status)

    statement = statement.order_by(Subtask.created_at.asc())

    return list(db.scalars(statement).all())


def create_subtask(
    db: Session,
    project_id: int,
    task_id: int,
    subtask_data: SubtaskCreate,
) -> Subtask:
    task = get_project_task_or_404(db, project_id, task_id)

    subtask = Subtask(
        task_id=task.id,
        **subtask_data.model_dump(),
    )

    db.add(subtask)

    try:
        db.commit()
        db.refresh(subtask)
    except Exception:
        db.rollback()
        raise

    return subtask


def update_subtask(
    db: Session,
    project_id: int,
    task_id: int,
    subtask_id: int,
    subtask_data: SubtaskUpdate,
) -> Subtask:
    subtask = get_task_subtask_or_404(db, project_id, task_id, subtask_id)
    update_data = subtask_data.model_dump(exclude_unset=True)

    required_fields = {"title", "description", "status"}

    for field, value in update_data.items():
        if field in required_fields and value is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Поле '{field}' не может быть пустым",
            )

        setattr(subtask, field, value)

    try:
        db.commit()
        db.refresh(subtask)
    except Exception:
        db.rollback()
        raise

    return subtask


def delete_subtask(
    db: Session,
    project_id: int,
    task_id: int,
    subtask_id: int,
) -> None:
    subtask = get_task_subtask_or_404(db, project_id, task_id, subtask_id)

    db.delete(subtask)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_task_story_point_or_404(
    db: Session,
    project_id: int,
    task_id: int,
) -> StoryPoint:
    get_project_task_or_404(db, project_id, task_id)

    story_point = db.scalar(
        select(StoryPoint).where(
            StoryPoint.project_id == project_id,
            StoryPoint.task_id == task_id,
        )
    )

    if story_point is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оценка задачи в сторипоинтах не найдена",
        )

    return story_point


def create_story_point(
    db: Session,
    project_id: int,
    task_id: int,
    story_point_data: StoryPointCreate,
) -> StoryPoint:
    task = get_project_task_or_404(db, project_id, task_id)

    existing_story_point = db.scalar(
        select(StoryPoint).where(StoryPoint.task_id == task_id)
    )

    if existing_story_point is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У задачи уже есть оценка в сторипоинтах",
        )

    story_point = StoryPoint(
        project_id=project_id,
        task_id=task.id,
        points=story_point_data.points,
    )

    db.add(story_point)

    try:
        db.commit()
        db.refresh(story_point)
    except Exception:
        db.rollback()
        raise

    return story_point


def update_story_point(
    db: Session,
    project_id: int,
    task_id: int,
    story_point_data: StoryPointUpdate,
) -> StoryPoint:
    story_point = get_task_story_point_or_404(db, project_id, task_id)

    story_point.points = story_point_data.points

    try:
        db.commit()
        db.refresh(story_point)
    except Exception:
        db.rollback()
        raise

    return story_point


def delete_story_point(
    db: Session,
    project_id: int,
    task_id: int,
) -> None:
    story_point = get_task_story_point_or_404(db, project_id, task_id)

    db.delete(story_point)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def get_project_story_points_total(
    db: Session,
    project_id: int,
) -> int:
    get_project_or_404(db, project_id)

    total = db.scalar(
        select(func.coalesce(func.sum(StoryPoint.points), 0))
        .where(StoryPoint.project_id == project_id)
    )

    return int(total)