import uuid

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


@router.post("/problems")
async def create_problem(
    source: str,
    title: str,
    difficulty: str,
    language: str,
    external_id: str | None = None,
    tags: list | None = None,
):
    problem_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO problems (
                    id,
                    source,
                    external_id,
                    title,
                    difficulty,
                    language,
                    tags
                )
                VALUES (
                    :id,
                    :source,
                    :external_id,
                    :title,
                    :difficulty,
                    :language,
                    :tags
                )
                RETURNING id
            """),
            {
                "id": problem_id,
                "source": source,
                "external_id": external_id,
                "title": title,
                "difficulty": difficulty,
                "language": language,
                "tags": tags,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/problems/{problem_id}")
async def get_problem(
    problem_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    source,
                    external_id,
                    title,
                    difficulty,
                    language,
                    tags
                FROM problems
                WHERE id = :id
            """),
            {
                "id": problem_id,
            },
        )

        problem = result.mappings().one_or_none()

    if problem is None:
        raise NotFoundError(
            f"No problem found for id={problem_id}"
        )

    return {
        "problem": dict(problem)
    }


@router.get("/problems")
async def list_problems(
    source: str | None = None,
    difficulty: str | None = None,
    language: str | None = None,
    skip: int = 0,
    limit: int = 100,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    source,
                    external_id,
                    title,
                    difficulty,
                    language,
                    tags
                FROM problems
                WHERE (:source IS NULL OR source = :source)
                  AND (:difficulty IS NULL OR difficulty = :difficulty)
                  AND (:language IS NULL OR language = :language)
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "source": source,
                "difficulty": difficulty,
                "language": language,
                "skip": skip,
                "limit": limit,
            },
        )

        problems = result.mappings().all()

    return {
        "problems": [
            dict(problem)
            for problem in problems
        ]
    }


@router.put("/problems/{problem_id}")
async def update_problem(
    problem_id: uuid.UUID,
    source: str | None = None,
    external_id: str | None = None,
    title: str | None = None,
    difficulty: str | None = None,
    language: str | None = None,
    tags: list | None = None,
):
    updates = {}

    if source is not None:
        updates["source"] = source

    if external_id is not None:
        updates["external_id"] = external_id

    if title is not None:
        updates["title"] = title

    if difficulty is not None:
        updates["difficulty"] = difficulty

    if language is not None:
        updates["language"] = language

    if tags is not None:
        updates["tags"] = tags

    if not updates:
        return {
            "id": problem_id,
            "status": "no changes",
        }

    set_clauses = ", ".join(
        f"{field} = :{field}"
        for field in updates
    )

    updates["id"] = problem_id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(f"""
                UPDATE problems
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No problem found for id={problem_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/problems/{problem_id}")
async def delete_problem(
    problem_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM problems
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": problem_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No problem found for id={problem_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }