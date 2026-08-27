import uuid

from datetime import datetime

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


@router.post("/user-lesson-progress")
async def create_user_lesson_progress(
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
    status: str = "not_started",
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
):
    progress_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO user_lesson_progress (
                    id,
                    user_id,
                    lesson_id,
                    status,
                    started_at,
                    completed_at
                )
                VALUES (
                    :id,
                    :user_id,
                    :lesson_id,
                    :status,
                    :started_at,
                    :completed_at
                )
                RETURNING id
            """),
            {
                "id": progress_id,
                "user_id": user_id,
                "lesson_id": lesson_id,
                "status": status,
                "started_at": started_at,
                "completed_at": completed_at,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/user-lesson-progress/{progress_id}")
async def get_user_lesson_progress(
    progress_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    lesson_id,
                    status,
                    started_at,
                    completed_at
                FROM user_lesson_progress
                WHERE id = :id
            """),
            {
                "id": progress_id,
            },
        )

        progress = result.mappings().one_or_none()

    if progress is None:
        raise NotFoundError(
            f"No lesson progress found for id={progress_id}"
        )

    return {
        "progress": dict(progress)
    }


@router.get("/user-lesson-progress/user/{user_id}/lesson/{lesson_id}")
async def get_user_lesson_progress_for(
    user_id: uuid.UUID,
    lesson_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    lesson_id,
                    status,
                    started_at,
                    completed_at
                FROM user_lesson_progress
                WHERE user_id = :user_id
                  AND lesson_id = :lesson_id
                LIMIT 1
            """),
            {
                "user_id": user_id,
                "lesson_id": lesson_id,
            },
        )

        progress = result.mappings().one_or_none()

    if progress is None:
        raise NotFoundError(
            f"No lesson progress found for "
            f"user_id={user_id}, lesson_id={lesson_id}"
        )

    return {
        "progress": dict(progress)
    }


@router.get("/user-lesson-progress")
async def list_user_lesson_progress(
    user_id: uuid.UUID | None = None,
    lesson_id: uuid.UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    lesson_id,
                    status,
                    started_at,
                    completed_at
                FROM user_lesson_progress
                WHERE (:user_id IS NULL OR user_id = :user_id)
                  AND (:lesson_id IS NULL OR lesson_id = :lesson_id)
                  AND (:status IS NULL OR status = :status)
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "user_id": user_id,
                "lesson_id": lesson_id,
                "status": status,
                "skip": skip,
                "limit": limit,
            },
        )

        progress_list = result.mappings().all()

    return {
        "progress": [
            dict(progress)
            for progress in progress_list
        ]
    }


@router.put("/user-lesson-progress/{progress_id}")
async def update_user_lesson_progress(
    progress_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    lesson_id: uuid.UUID | None = None,
    status: str | None = None,
    started_at: datetime | None = None,
    completed_at: datetime | None = None,
):
    updates = {}

    if user_id is not None:
        updates["user_id"] = user_id

    if lesson_id is not None:
        updates["lesson_id"] = lesson_id

    if status is not None:
        updates["status"] = status

    if started_at is not None:
        updates["started_at"] = started_at

    if completed_at is not None:
        updates["completed_at"] = completed_at

    if not updates:
        return {
            "id": progress_id,
            "status": "no changes",
        }

    set_clauses = ", ".join(
        f"{field} = :{field}"
        for field in updates
    )

    updates["id"] = progress_id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(f"""
                UPDATE user_lesson_progress
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No lesson progress found for id={progress_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/user-lesson-progress/{progress_id}")
async def delete_user_lesson_progress(
    progress_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM user_lesson_progress
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": progress_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No lesson progress found for id={progress_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }