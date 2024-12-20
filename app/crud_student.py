"""
crud_students.py

This module provides CRUD operations for managing question and scoring submissions
in the database using SQLAlchemy and FastAPI.

Functions:
    add_question_submission(
        db: Session,
        submission: schemas.QuestionSubmission,
    ) -> models.QuestionSubmission:
        Adds a question submission to the database and associates it with an assignment.

    add_scoring_submission(
        db: Session,
        submission: schemas.ScoringSubmission,
        score: Score,
    ) -> models.ScoringSubmission:
        Adds a scoring submission to the database and associates it with an assignment.

Dependencies:
    - FastAPI for HTTP exception handling and status codes.
    - SQLAlchemy for database interaction.
    - models and schemas modules for defining database models and input schemas.
    - live_scorer.Score for representing score-related data.
"""

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas
from .live_scorer import Score


def add_question_submission(
    db: Session,
    submission: schemas.QuestionSubmission,
):
    """
    Adds a question submission to the database.

    Args:
        db (Session): The database session.
        submission (schemas.QuestionSubmission): The submission data containing student email, assignment, question, responses, and score.

    Raises:
        HTTPException: If the assignment is not found in the database.

    Returns:
        models.QuestionSubmission: The newly created question submission record.
    """
    assignment_title = f"{submission.term}_{submission.assignment}"

    stmt = select(models.Assignment).where(models.Assignment.title == assignment_title)
    db_assignment = db.execute(stmt).scalar_one_or_none()
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assignment not found in database",
        )

    db_submission = models.QuestionSubmission(
        student_email=submission.student_email,
        assignment=assignment_title,
        question=submission.question,
        responses=submission.responses,
        max_points=submission.score.max_points,
        points_earned=submission.score.points_earned,
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission


def add_scoring_submission(
    db: Session,
    submission: schemas.ScoringSubmission,
    score: Score,
):
    """
    Add a scoring submission to the database.

    Args:
        db (Session): The database session to use for the operation.
        submission (schemas.ScoringSubmission): The scoring submission data.
        score (Score): The score details including max points and points earned.

    Raises:
        HTTPException: If the assignment is not found in the database.

    Returns:
        models.ScoringSubmission: The newly created scoring submission record.
    """
    assignment_title = f"{submission.term}_{submission.assignment}"

    stmt = select(models.Assignment).where(models.Assignment.title == assignment_title)
    db_assignment = db.execute(stmt).scalar_one_or_none()
    if not db_assignment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Assignment not found in database",
        )

    db_submission = models.ScoringSubmission(
        student_email=submission.student_email,
        assignment=assignment_title,
        question=submission.question,
        max_points=score.max_points,
        points_earned=score.points_earned,
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission
