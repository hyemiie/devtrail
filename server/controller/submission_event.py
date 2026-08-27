import uuid

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


# Submission events are immutable snapshots.
# They can only be created, read, or deleted.
# There is intentionally no update endpoint.


@router.post("/submission-events")
async def create_submission_event(
    submission_id: uuid.UUID,
    event_type: str,
    code_snapshot: str,
):
    event_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO submission_events (
                    id,
                    submission_id,
                    event_type,
                    code_snapshot
                )
                VALUES (
                    :id,
                    :submission_id,
                    :event_type,
                    :code_snapshot
                )
                RETURNING id
            """),
            {
                "id": event_id,
                "submission_id": submission_id,
                "event_type": event_type,
                "code_snapshot": code_snapshot,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/submission-events/{event_id}")
async def get_submission_event(
    event_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    submission_id,
                    event_type,
                    code_snapshot,
                    created_at
                FROM submission_events
                WHERE id = :id
            """),
            {
                "id": event_id,
            },
        )

        event = result.mappings().one_or_none()

    if event is None:
        raise NotFoundError(
            f"No submission event found for id={event_id}"
        )

    return {
        "event": dict(event)
    }


@router.get("/submission-events")
async def list_submission_events(
    submission_id: uuid.UUID | None = None,
    event_type: str | None = None,
    skip: int = 0,
    limit: int = 500,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    submission_id,
                    event_type,
                    code_snapshot,
                    created_at
                FROM submission_events
                WHERE (
                    :submission_id IS NULL
                    OR submission_id = :submission_id
                )
                AND (
                    :event_type IS NULL
                    OR event_type = :event_type
                )
                ORDER BY created_at ASC
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "submission_id": submission_id,
                "event_type": event_type,
                "skip": skip,
                "limit": limit,
            },
        )

        events = result.mappings().all()

    return {
        "events": [
            dict(event)
            for event in events
        ]
    }


@router.delete("/submission-events/{event_id}")
async def delete_submission_event(
    event_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM submission_events
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": event_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No submission event found for id={event_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }