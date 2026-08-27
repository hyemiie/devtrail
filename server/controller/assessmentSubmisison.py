import uuid

from fastapi import APIRouter

from db.session import AsyncSessionLocal
from core.errors import NotFoundError
from sqlalchemy import text


router = APIRouter()


@router.post("/assessment-submissions")
async def create_assessment_submission(
    user_id: uuid.UUID,
    assessment_id: uuid.UUID,
    status: str = "submitted",
    score: float | None = None,
    feedback: str | None = None,
    reasoning_score: float | None = None,
    reasoning_feedback: str | None = None,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO assessment_submissions (
                    id,
                    user_id,
                    assessment_id,
                    status,
                    score,
                    feedback,
                    reasoning_score,
                    reasoning_feedback
                )
                VALUES (
                    :id,
                    :user_id,
                    :assessment_id,
                    :status,
                    :score,
                    :feedback,
                    :reasoning_score,
                    :reasoning_feedback
                )
                RETURNING id
            """),
            {
                "id": uuid.uuid4(),
                "user_id": user_id,
                "assessment_id": assessment_id,
                "status": status,
                "score": score,
                "feedback": feedback,
                "reasoning_score": reasoning_score,
                "reasoning_feedback": reasoning_feedback,
            },
        )

        submission_id = result.scalar_one()
        await session.commit()

    return {
        "id": submission_id,
        "status": "created",
    }


@router.get("/assessment-submissions/{submission_id}")
async def get_assessment_submission(submission_id: uuid.UUID):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    user_id,
                    assessment_id,
                    status,
                    score,
                    feedback,
                    reasoning_score,
                    reasoning_feedback,
                    submitted_at
                FROM assessment_submissions
                WHERE id = :id
            """),
            {"id": submission_id},
        )

        submission = result.mappings().one_or_none()

    if submission is None:
        raise NotFoundError(
            f"No assessment submission found for id={submission_id}"
        )

    return {
        "submission": dict(submission)
    }


@router.get("/assessment-submissions")
async def list_assessment_submissions(
    user_id: uuid.UUID | None = None,
    assessment_id: uuid.UUID | None = None,
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
                    assessment_id,
                    status,
                    score,
                    feedback,
                    reasoning_score,
                    reasoning_feedback,
                    submitted_at
                FROM assessment_submissions
                WHERE (:user_id IS NULL OR user_id = :user_id)
                  AND (:assessment_id IS NULL OR assessment_id = :assessment_id)
                  AND (:status IS NULL OR status = :status)
                ORDER BY submitted_at DESC
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "user_id": user_id,
                "assessment_id": assessment_id,
                "status": status,
                "skip": skip,
                "limit": limit,
            },
        )

        submissions = result.mappings().all()

    return {
        "submissions": [dict(submission) for submission in submissions]
    }


@router.put("/assessment-submissions/{submission_id}")
async def update_assessment_submission(
    submission_id: uuid.UUID,
    status: str | None = None,
    score: float | None = None,
    feedback: str | None = None,
    reasoning_score: float | None = None,
    reasoning_feedback: str | None = None,
):
    updates = {}

    if status is not None:
        updates["status"] = status

    if score is not None:
        updates["score"] = score

    if feedback is not None:
        updates["feedback"] = feedback

    if reasoning_score is not None:
        updates["reasoning_score"] = reasoning_score

    if reasoning_feedback is not None:
        updates["reasoning_feedback"] = reasoning_feedback

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
                UPDATE assessment_submissions
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No assessment submission found for id={submission_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/assessment-submissions/{submission_id}")
async def delete_assessment_submission(
    submission_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM assessment_submissions
                WHERE id = :id
                RETURNING id
            """),
            {"id": submission_id},
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No assessment submission found for id={submission_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }