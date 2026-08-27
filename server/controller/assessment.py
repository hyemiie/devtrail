import uuid

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


@router.post("/assessments")
async def create_assessment(
    type: str,
    title: str,
    lesson_id: uuid.UUID | None = None,
    description: str | None = None,
    week_number: int | None = None,
    requirements: dict | None = None,
    max_score: float | None = None,
):
    assessment_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO assessments (
                    id,
                    lesson_id,
                    type,
                    title,
                    description,
                    week_number,
                    requirements,
                    max_score
                )
                VALUES (
                    :id,
                    :lesson_id,
                    :type,
                    :title,
                    :description,
                    :week_number,
                    :requirements,
                    :max_score
                )
                RETURNING id
            """),
            {
                "id": assessment_id,
                "lesson_id": lesson_id,
                "type": type,
                "title": title,
                "description": description,
                "week_number": week_number,
                "requirements": requirements,
                "max_score": max_score,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/assessments/{assessment_id}")
async def get_assessment(
    assessment_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    lesson_id,
                    type,
                    title,
                    description,
                    week_number,
                    requirements,
                    max_score
                FROM assessments
                WHERE id = :id
            """),
            {
                "id": assessment_id,
            },
        )

        assessment = result.mappings().one_or_none()

    if assessment is None:
        raise NotFoundError(
            f"No assessment found for id={assessment_id}"
        )

    return {
        "assessment": dict(assessment)
    }


@router.get("/assessments")
async def list_assessments(
    lesson_id: uuid.UUID | None = None,
    type: str | None = None,
    week_number: int | None = None,
    skip: int = 0,
    limit: int = 100,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    lesson_id,
                    type,
                    title,
                    description,
                    week_number,
                    requirements,
                    max_score
                FROM assessments
                WHERE (:lesson_id IS NULL OR lesson_id = :lesson_id)
                  AND (:type IS NULL OR type = :type)
                  AND (:week_number IS NULL OR week_number = :week_number)
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "lesson_id": lesson_id,
                "type": type,
                "week_number": week_number,
                "skip": skip,
                "limit": limit,
            },
        )

        assessments = result.mappings().all()

    return {
        "assessments": [
            dict(assessment)
            for assessment in assessments
        ]
    }


@router.put("/assessments/{assessment_id}")
async def update_assessment(
    assessment_id: uuid.UUID,
    type: str | None = None,
    title: str | None = None,
    lesson_id: uuid.UUID | None = None,
    description: str | None = None,
    week_number: int | None = None,
    requirements: dict | None = None,
    max_score: float | None = None,
):
    updates = {}

    if type is not None:
        updates["type"] = type

    if title is not None:
        updates["title"] = title

    if lesson_id is not None:
        updates["lesson_id"] = lesson_id

    if description is not None:
        updates["description"] = description

    if week_number is not None:
        updates["week_number"] = week_number

    if requirements is not None:
        updates["requirements"] = requirements

    if max_score is not None:
        updates["max_score"] = max_score

    if not updates:
        return {
            "id": assessment_id,
            "status": "no changes",
        }

    set_clauses = ", ".join(
        f"{field} = :{field}"
        for field in updates
    )

    updates["id"] = assessment_id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(f"""
                UPDATE assessments
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No assessment found for id={assessment_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/assessments/{assessment_id}")
async def delete_assessment(
    assessment_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM assessments
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": assessment_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No assessment found for id={assessment_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }