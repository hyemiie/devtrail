import uuid
from datetime import datetime

from sqlalchemy import (
    String,
    Text,
    Boolean,
    Integer,
    ForeignKey,
    Numeric,
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


# ─────────────────────────────────────────────────────────────
# Users
# ─────────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    current_level: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="user",
    )

    lesson_progress: Mapped[list["UserLessonProgress"]] = relationship(
        back_populates="user",
    )

    assessment_submissions: Mapped[list["AssessmentSubmission"]] = relationship(
        back_populates="user",
    )

    chat_rooms: Mapped[list["ChatRoom"]] = relationship(
        back_populates="user",
    )

    __table_args__ = (
        CheckConstraint(
            "current_level IN ('beginner', 'intermediate', 'advanced')",
            name="ck_users_current_level",
        ),
    )


# ─────────────────────────────────────────────────────────────
# Problems / coding submissions
# ─────────────────────────────────────────────────────────────

class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    source: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    external_id: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    difficulty: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    tags: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    submissions: Mapped[list["Submission"]] = relationship(
        back_populates="problem",
    )

    __table_args__ = (
        CheckConstraint(
            "source IN ('leetcode', 'custom')",
            name="ck_problems_source",
        ),
        CheckConstraint(
            "difficulty IN ('easy', 'medium', 'hard')",
            name="ck_problems_difficulty",
        ),
        CheckConstraint(
            "language IN ('python', 'javascript')",
            name="ck_problems_language",
        ),
    )


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    problem_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("problems.id"),
        nullable=False,
    )

    code: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    commit_sha: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="submissions",
    )

    problem: Mapped["Problem"] = relationship(
        back_populates="submissions",
    )

    events: Mapped[list["SubmissionEvent"]] = relationship(
        back_populates="submission",
    )

    __table_args__ = (
        CheckConstraint(
            "language IN ('python', 'javascript', go)",
            name="ck_submissions_language",
        ),
        CheckConstraint(
            "status IN ('passed', 'failed', 'pending')",
            name="ck_submissions_status",
        ),
    )


class SubmissionEvent(Base):
    """
    Intermediate edit/keystroke snapshots from the IDE session.
    Used to reconstruct the user's actual problem-solving process.
    """

    __tablename__ = "submission_events"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("submissions.id"),
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    code_snapshot: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    submission: Mapped["Submission"] = relationship(
        back_populates="events",
    )


# ─────────────────────────────────────────────────────────────
# Lessons / curriculum progress
# ─────────────────────────────────────────────────────────────

class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    level: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    progress: Mapped[list["UserLessonProgress"]] = relationship(
        back_populates="lesson",
    )

    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="lesson",
    )

    __table_args__ = (
        CheckConstraint(
            "language IN ('python', 'javascript')",
            name="ck_lessons_language",
        ),
        CheckConstraint(
            "level IN ('beginner', 'intermediate', 'advanced')",
            name="ck_lessons_level",
        ),
    )


class UserLessonProgress(Base):
    __tablename__ = "user_lesson_progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="not_started",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        nullable=True,
    )

    user: Mapped["User"] = relationship(
        back_populates="lesson_progress",
    )

    lesson: Mapped["Lesson"] = relationship(
        back_populates="progress",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "lesson_id",
            name="uq_user_lesson_progress",
        ),
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed')",
            name="ck_user_lesson_progress_status",
        ),
    )


# ─────────────────────────────────────────────────────────────
# Assessments
#
# One generic concept for:
#   - diagnostic quizzes
#   - checkpoint tests
#   - weekly quizzes
#   - weekly projects
#   - major projects
#
# An assessment can have zero or many items.
# ─────────────────────────────────────────────────────────────

class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    lesson_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("lessons.id"),
        nullable=True,
    )

    type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    week_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    requirements: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    max_score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    lesson: Mapped["Lesson | None"] = relationship(
        back_populates="assessments",
    )

    items: Mapped[list["AssessmentItem"]] = relationship(
        back_populates="assessment",
    )

    submissions: Mapped[list["AssessmentSubmission"]] = relationship(
        back_populates="assessment",
    )

    __table_args__ = (
        CheckConstraint(
            """
            type IN (
                'diagnostic',
                'checkpoint',
                'weekly_quiz',
                'weekly_project',
                'major_project'
            )
            """,
            name="ck_assessments_type",
        ),
    )


class AssessmentItem(Base):
    """
    A graded item within an assessment.

    Quiz/test:
        question + options + correct_answer + expected_reasoning

    Project:
        these fields can be NULL and the assessment can be graded
        holistically through the parent AssessmentSubmission.
    """

    __tablename__ = "assessment_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id"),
        nullable=False,
    )

    title: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    question: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    options: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
    )

    correct_answer: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )

    expected_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    max_score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    order_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    assessment: Mapped["Assessment"] = relationship(
        back_populates="items",
    )

    submissions: Mapped[list["AssessmentItemSubmission"]] = relationship(
        back_populates="item",
    )

    __table_args__ = (
        UniqueConstraint(
            "assessment_id",
            "order_index",
            name="uq_assessment_item_order",
        ),
    )


class AssessmentSubmission(Base):
    """
    A user's submission for an entire assessment.

    For a quiz:
        one AssessmentSubmission represents the quiz attempt.

    For a project:
        one AssessmentSubmission represents the project submission.

    Grading can be:
        - item-level through AssessmentItemSubmission
        - holistic through score / feedback on this table.
    """

    __tablename__ = "assessment_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessments.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="submitted",
    )

    score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    reasoning_score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    reasoning_feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="assessment_submissions",
    )

    assessment: Mapped["Assessment"] = relationship(
        back_populates="submissions",
    )

    item_submissions: Mapped[list["AssessmentItemSubmission"]] = relationship(
        back_populates="assessment_submission",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('in_progress', 'submitted', 'graded')",
            name="ck_assessment_submissions_status",
        ),
    )


class AssessmentItemSubmission(Base):
    """
    The user's response to one assessment item.

    This is primarily useful for quizzes/tests, but also supports
    project checklists or other itemized assessments.
    """

    __tablename__ = "assessment_item_submissions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    assessment_submission_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessment_submissions.id"),
        nullable=False,
    )

    item_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("assessment_items.id"),
        nullable=False,
    )

    submitted_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    submitted_reasoning: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    answer_correct: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )

    score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    reasoning_score: Mapped[float | None] = mapped_column(
        Numeric,
        nullable=True,
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    submitted_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    assessment_submission: Mapped["AssessmentSubmission"] = relationship(
        back_populates="item_submissions",
    )

    item: Mapped["AssessmentItem"] = relationship(
        back_populates="submissions",
    )

    __table_args__ = (
        UniqueConstraint(
            "assessment_submission_id",
            "item_id",
            name="uq_assessment_item_submission",
        ),
    )


# ─────────────────────────────────────────────────────────────
# Chat
# ─────────────────────────────────────────────────────────────

class ChatRoom(Base):
    __tablename__ = "chat_rooms"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    context_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    context_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship(
        back_populates="chat_rooms",
    )

    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="room",
    )

    __table_args__ = (
        CheckConstraint(
            "context_type IN ('lesson', 'problem', 'assessment', 'general')",
            name="ck_chat_rooms_context_type",
        ),
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    room_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_rooms.id"),
        nullable=False,
    )

    sender: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
    )

    room: Mapped["ChatRoom"] = relationship(
        back_populates="messages",
    )

    __table_args__ = (
        CheckConstraint(
            "sender IN ('user', 'ai')",
            name="ck_chat_messages_sender",
        ),
    )