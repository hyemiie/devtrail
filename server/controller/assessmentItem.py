import uuid

from fastapi import APIRouter

from sqlalchemy import text

from db.session import AsyncSessionLocal
from core.errors import NotFoundError


router = APIRouter()


@router.post("/assessment-items")
async def create_assessment_item(
    assessment_id: uuid.UUID,
    order_index: int,
    title: str | None = None,
    question: str | None = None,
    options: list | None = None,
    correct_answer: str | None = None,
    expected_reasoning: str | None = None,
    max_score: float | None = None,
):
    item_id = uuid.uuid4()

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO assessment_items (
                    id,
                    assessment_id,
                    title,
                    question,
                    options,
                    correct_answer,
                    expected_reasoning,
                    max_score,
                    order_index
                )
                VALUES (
                    :id,
                    :assessment_id,
                    :title,
                    :question,
                    :options,
                    :correct_answer,
                    :expected_reasoning,
                    :max_score,
                    :order_index
                )
                RETURNING id
            """),
            {
                "id": item_id,
                "assessment_id": assessment_id,
                "title": title,
                "question": question,
                "options": options,
                "correct_answer": correct_answer,
                "expected_reasoning": expected_reasoning,
                "max_score": max_score,
                "order_index": order_index,
            },
        )

        created_id = result.scalar_one()

        await session.commit()

    return {
        "id": created_id,
        "status": "created",
    }


@router.get("/assessment-items/{item_id}")
async def get_assessment_item(
    item_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    assessment_id,
                    title,
                    question,
                    options,
                    correct_answer,
                    expected_reasoning,
                    max_score,
                    order_index
                FROM assessment_items
                WHERE id = :id
            """),
            {
                "id": item_id,
            },
        )

        item = result.mappings().one_or_none()

    if item is None:
        raise NotFoundError(
            f"No assessment item found for id={item_id}"
        )

    return {
        "item": dict(item)
    }


@router.get("/assessment-items")
async def list_assessment_items(
    assessment_id: uuid.UUID | None = None,
    skip: int = 0,
    limit: int = 100,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT
                    id,
                    assessment_id,
                    title,
                    question,
                    options,
                    correct_answer,
                    expected_reasoning,
                    max_score,
                    order_index
                FROM assessment_items
                WHERE (
                    :assessment_id IS NULL
                    OR assessment_id = :assessment_id
                )
                ORDER BY order_index ASC
                OFFSET :skip
                LIMIT :limit
            """),
            {
                "assessment_id": assessment_id,
                "skip": skip,
                "limit": limit,
            },
        )

        items = result.mappings().all()

    return {
        "items": [
            dict(item)
            for item in items
        ]
    }


@router.put("/assessment-items/{item_id}")
async def update_assessment_item(
    item_id: uuid.UUID,
    assessment_id: uuid.UUID | None = None,
    order_index: int | None = None,
    title: str | None = None,
    question: str | None = None,
    options: list | None = None,
    correct_answer: str | None = None,
    expected_reasoning: str | None = None,
    max_score: float | None = None,
):
    updates = {}

    if assessment_id is not None:
        updates["assessment_id"] = assessment_id

    if order_index is not None:
        updates["order_index"] = order_index

    if title is not None:
        updates["title"] = title

    if question is not None:
        updates["question"] = question

    if options is not None:
        updates["options"] = options

    if correct_answer is not None:
        updates["correct_answer"] = correct_answer

    if expected_reasoning is not None:
        updates["expected_reasoning"] = expected_reasoning

    if max_score is not None:
        updates["max_score"] = max_score

    if not updates:
        return {
            "id": item_id,
            "status": "no changes",
        }

    set_clauses = ", ".join(
        f"{field} = :{field}"
        for field in updates
    )

    updates["id"] = item_id

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text(f"""
                UPDATE assessment_items
                SET {set_clauses}
                WHERE id = :id
                RETURNING id
            """),
            updates,
        )

        updated_id = result.scalar_one_or_none()

        if updated_id is None:
            raise NotFoundError(
                f"No assessment item found for id={item_id}"
            )

        await session.commit()

    return {
        "id": updated_id,
        "status": "updated",
    }


@router.delete("/assessment-items/{item_id}")
async def delete_assessment_item(
    item_id: uuid.UUID,
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                DELETE FROM assessment_items
                WHERE id = :id
                RETURNING id
            """),
            {
                "id": item_id,
            },
        )

        deleted_id = result.scalar_one_or_none()

        if deleted_id is None:
            raise NotFoundError(
                f"No assessment item found for id={item_id}"
            )

        await session.commit()

    return {
        "id": deleted_id,
        "status": "deleted",
    }