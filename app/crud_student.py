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
from sqlalchemy import select, func
from sqlalchemy.orm import Session
import numpy as np

from datetime import datetime
from typing import Optional


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


def get_assignments_by_week_and_type(
    db: Session, week_number: int, assignment_type: str
) -> list[models.Assignment]:
    """
    Retrieve assignments from the database based on week number and assignment type.

    Args:
        db (Session): The database session to use for the query.
        week_number (int): The week number to filter assignments by.
        assignment_type (str): The type of assignments to retrieve.

    Returns:
        list[models.Assignment]: A list of assignment objects matching the criteria.
    """
    stmt = select(models.Assignment).where(
        models.Assignment.week_number == week_number,
        models.Assignment.assignment_type == assignment_type,
    )
    return db.execute(stmt).scalars().one_or_none()


def get_max_score_and_due_date_by_week_and_type(
    db: Session, week_number: int, assignment_type: str
) -> tuple[Optional[float], Optional[datetime]]:
    """
    Retrieve the maximum score and latest due date for assignments based on week number and type.

    Args:
        db (Session): The database session to use for the query.
        week_number (int): The week number to filter assignments by.
        assignment_type (str): The type of assignments to retrieve.

    Returns:
        tuple[Optional[float], Optional[datetime]]: A tuple containing the maximum score
        and the latest due date for the matching assignments. Returns (None, None) if no match is found.
    """
    stmt = select(
        func.max(models.Assignment.max_score), func.max(models.Assignment.due_date)
    ).where(
        models.Assignment.week_number == week_number,
        models.Assignment.assignment_type == assignment_type,
    )
    result = db.execute(stmt).one_or_none()
    return result if result else (None, None)


def calculate_time_delta_in_seconds(timestamp1_str: str, timestamp2_str: str) -> int:
    """
    Calculate the time delta between two timestamps in seconds.

    Args:
        timestamp1_str (str): The first timestamp in the format "YYYY-MM-DD HH:MM:SS TZ".
        timestamp2_str (str): The second timestamp in the format "YYYY-MM-DD HH:MM:SS TZ".

    Returns:
        int: The time delta between the two timestamps in seconds.
    """

    # Parse the timestamps into datetime objects with the timezone
    timestamp1 = datetime.strptime(timestamp1_str, "%Y-%m-%d %H:%M:%S %Z")
    timestamp2 = datetime.strptime(timestamp2_str, "%Y-%m-%d %H:%M:%S %Z")

    # Calculate the time delta
    time_delta = timestamp2 - timestamp1

    # Return the time delta in seconds
    return int(time_delta.total_seconds())


def get_modified_grade_percentage(time_delta: int) -> float:
    """
    Calculate the grade modifier based on the time delta between two timestamps.

    Args:
        time_delta (int): The time delta between two timestamps in seconds.

    Returns:
        float: The grade modifier percentage based on the time delta.
    """

    # Parameters
    Q0 = 100  # Initial quantity
    Q_min = 40  # Minimum grade/quantity
    k = 6.88e-5  # Decay constant per minute

    # Exponential decay function with piecewise definition
    Q = Q0 * np.exp(-k * time_delta / 60)  # Convert seconds to minutes
    Q = np.maximum(Q, Q_min)  # Apply floor condition
    Q = np.minimum(Q, 100)  # Apply ceiling condition

    return Q


# def get_assignment_by_title(db: Session, title: str) -> Optional[models.Assignment]:
#     """
#     Retrieve an assignment from the database by its title.

#     Args:
#         db (Session): The database session to use for the query.
#         title (str): The title of the assignment to retrieve.

#     Returns:
#         Optional[models.Assignment]: The assignment object if found, otherwise None.
#     """
#     stmt = select(models.Assignment).where(models.Assignment.title == title)
#     return db.execute(stmt).scalar_one_or_none()
