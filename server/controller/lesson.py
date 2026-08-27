import uuid

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


@router.post("/lessons")
async def create_lesson(
    title: str,
    content: str,
    order_index: int,
    language: str,
    level: str,
):
    lesson_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO lessons (
                    id,
                    title,
                    content,
                    order_index,
                    language,
                    level
                )
                VALUES (
                    :id,
                    :title,
                    :content,
                    :order_index,
                    :language,
                    :level
                )
                RETURNING id
            """),
            {
                "id": lesson_id,
                "title": title,
                "content": content,
                "order_index": order_index,
                "language": language,
                "level": level,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/lessons/{lesson_id}")
async def get_lesson(
    lesson_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    title,
                    content,
                    order_index,
                    language,
                    level
                FROM lessons
                WHERE id = :id
            """),
            {
                "id": lesson_id,
            },
        )

        lesson = result.mappings().one_or_none()

    if lesson is None:
        raise NotFoundError(
            f"No lesson found for id={lesson_id}"
        )

    return {
        "lesson": dict(lesson)
    }


@router.get("/lessons")
async def list_lessons(
    language: str | None = None,
    level: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    title,
                    content,
                    order_index,
                    language,
                    level
                FROM lessons
                WHERE (:language IS NULL OR language = :language)
                  AND (:level IS NULL OR level = :level)
                ORDER BY order_index ASC
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "language": language,
                "level": level,
                "skip": skip,
                "limit": limit,
            },
        )

        lessons = result.mappings().all()

    return {
        "lessons": [
            dict(lesson)
            for lesson in lessons
        ]
    }


@router.put("/lessons/{lesson_id}")
async def update_lesson(
    lesson_id: uuid.UUID,
    title: str | None = None,
    content: str | None = None,
    order_index: int | None = None,
    language: str | None = None,
    level: str | None = None,
):
    updates = {}

    if title is not None:
        updates["title"] = title

    if content is not None:
        updates["content"] = content

    if order_index is not None:
        updates["order_index"] = order_index

    if language is not None:
        updates["language"] = language

    if level is not None:
        updates["level"] = level

    if not updates:
        return {
            "id": lesson_id,
            "status": "no changes",
        }

    set_clauses = ", ".join(
        f"{field} = :{field}"
        for field in updates
    )

    updates["id"] = lesson_id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(f"""
                UPDATE lessons
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No lesson found for id={lesson_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM lessons
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": lesson_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No lesson found for id={lesson_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }