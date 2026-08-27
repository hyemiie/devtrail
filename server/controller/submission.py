import uuid

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


@router.post("/submissions")
async def create_submission(
    user_id: uuid.UUID,
    problem_id: uuid.UUID,
    code: str,
    language: str,
    status: str = "pending",
    commit_sha: str | None = None,
):
    submission_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO submissions (
                    id,
                    user_id,
                    problem_id,
                    code,
                    language,
                    status,
                    commit_sha
                )
                VALUES (
                    :id,
                    :user_id,
                    :problem_id,
                    :code,
                    :language,
                    :status,
                    :commit_sha
                )
                RETURNING id
            """),
            {
                "id": submission_id,
                "user_id": user_id,
                "problem_id": problem_id,
                "code": code,
                "language": language,
                "status": status,
                "commit_sha": commit_sha,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/submissions/{submission_id}")
async def get_submission(
    submission_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    problem_id,
                    code,
                    language,
                    status,
                    commit_sha,
                    submitted_at
                FROM submissions
                WHERE id = :id
            """),
            {
                "id": submission_id,
            },
        )

        submission = result.mappings().one_or_none()

    if submission is None:
        raise NotFoundError(
            f"No submission found for id={submission_id}"
        )

    return {
        "submission": dict(submission)
    }


@router.get("/submissions")
async def list_submissions(
    user_id: uuid.UUID | None = None,
    problem_id: uuid.UUID | None = None,
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
                    problem_id,
                    code,
                    language,
                    status,
                    commit_sha,
                    submitted_at
                FROM submissions
                WHERE (:user_id IS NULL OR user_id = :user_id)
                  AND (:problem_id IS NULL OR problem_id = :problem_id)
                  AND (:status IS NULL OR status = :status)
                ORDER BY submitted_at DESC
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "user_id": user_id,
                "problem_id": problem_id,
                "status": status,
                "skip": skip,
                "limit": limit,
            },
        )

        submissions = result.mappings().all()

    return {
        "submissions": [
            dict(submission)
            for submission in submissions
        ]
    }


@router.put("/submissions/{submission_id}")
async def update_submission(
    submission_id: uuid.UUID,
    user_id: uuid.UUID | None = None,
    problem_id: uuid.UUID | None = None,
    code: str | None = None,
    language: str | None = None,
    status: str | None = None,
    commit_sha: str | None = None,
):
    updates = {}

    if user_id is not None:
        updates["user_id"] = user_id

    if problem_id is not None:
        updates["problem_id"] = problem_id

    if code is not None:
        updates["code"] = code

    if language is not None:
        updates["language"] = language

    if status is not None:
        updates["status"] = status

    if commit_sha is not None:
        updates["commit_sha"] = commit_sha

    if not updates:
        return {
            "id": submission_id,
            "status": "no changes",
        }

    set_clauses = ", ".join(
        f"{field} = :{field}"
        for field in updates
    )

    updates["id"] = submission_id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(f"""
                UPDATE submissions
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No submission found for id={submission_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/submissions/{submission_id}")
async def delete_submission(
    submission_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM submissions
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": submission_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No submission found for id={submission_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }