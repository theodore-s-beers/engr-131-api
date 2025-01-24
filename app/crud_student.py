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

import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from . import models, schemas
from . import crud_admin
from .live_scorer import Score

#
# Create
#


def add_notebook_submission(db: Session, submission: schemas.NotebookSubmission):
    db_submission = models.NotebookSubmission(
        student_email=submission.student_email,
        notebook=submission.notebook,
        week_number=submission.week_number,
        assignment_type=submission.assignment_type,
        timestamp=submission.timestamp,
        student_seed=submission.student_seed,
        due_date=submission.due_date,
        raw_score=submission.raw_score,
        late_assignment_percentage=submission.late_assignment_percentage,
        submitted_score=submission.submitted_score,
        current_max_score=submission.current_max_score,
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission


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


def add_submitted_assignment_score(
    db: Session, submission: schemas.AssignmentSubmission
):
    db_submission = models.AssignmentSubmission(
        student_email=submission.student_email,
        assignment=submission.assignment,
        week_number=submission.week_number,
        assignment_type=submission.assignment_type,
        timestamp=submission.timestamp,
        student_seed=submission.student_seed,
        due_date=submission.due_date,
        raw_score=submission.raw_score,
        late_assignment_percentage=submission.late_assignment_percentage,
        submitted_score=submission.submitted_score,
        current_max_score=submission.current_max_score,
    )

    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)

    return db_submission


#
# Read
#


def get_assignments_by_week_and_type(
    db: Session, week_number: int, assignment_type: str
) -> Optional[models.Assignment]:
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


def get_best_score(
    db: Session, student_email: str, assignment: str
) -> Optional[models.AssignmentSubmission]:
    """
    Retrieve the best score for a student on a specific assignment.

    Args:
        db (Session): The database session to use for the query.
        student_email (str): The email of the student.
        assignment (str): The title of the assignment.

    Returns:
        Optional[models.AssignmentSubmission]: The best assignment submission for the student,
        or None if no submission exists.
    """
    # Query to get the best score (highest `submitted_score`) for the given student and assignment
    stmt = (
        select(models.AssignmentSubmission)
        .where(
            models.AssignmentSubmission.student_email == student_email,
            models.AssignmentSubmission.assignment == assignment,
        )
        .order_by(models.AssignmentSubmission.submitted_score.desc())
        .limit(1)  # Limit to 1 to explicitly fetch the best
    )

    # Execute the query and return the first result
    result = db.execute(stmt).scalars().first()
    return result


def get_max_score_and_due_date_by_week_and_type(
    db: Session, week_number: int, assignment_type: str
) -> tuple[Optional[float], Optional[datetime.datetime]]:
    """
    Retrieve the maximum score and latest due date for assignments based on week number and type.

    Args:
        db (Session): The database session to use for the query.
        week_number (int): The week number to filter assignments by.
        assignment_type (str): The type of assignments to retrieve.

    Returns:
        tuple[Optional[float], Optional[datetime.datetime]]: A tuple containing the maximum score
        and the latest due date for the matching assignments. Returns (None, None) if no match is found.
    """
    stmt = select(
        func.max(models.Assignment.max_score), func.max(models.Assignment.due_date)
    ).where(
        models.Assignment.week_number == week_number,
        models.Assignment.assignment_type == assignment_type,
    )
    result = db.execute(stmt).one_or_none()
    return (result[0], result[1]) if result else (None, None)


def get_my_grades(db: Session, student_email: str) -> dict[str, float]:
    """
    Retrieve the best score for each assignment for a given student

    :param db: SQLAlchemy session
    :param student_email: Email prefix of the student whose grades are to be fetched
    :return: Dictionary mapping assignments to their best scores
    """

    stmt = (
        select(
            models.AssignmentSubmission.assignment,
            func.max(models.AssignmentSubmission.submitted_score).label("best_score"),
        )
        .where(models.AssignmentSubmission.student_email == student_email)
        .group_by(models.AssignmentSubmission.assignment)
    )

    best_scores = db.execute(stmt).all()
    return {assignment: best_score for assignment, best_score in best_scores}


def get_my_grades_testing(db: Session, student_email: str):

    return crud_admin.get_assignments(db)

def get_notebook_by_title(db: Session, title: str) -> Optional[models.Notebook]:
    """
    Retrieve a notebook from the database by its title.

    Args:
        db (Session): The database session to use for the query.
        title (str): The title of the notebook to retrieve.

    Returns:
        Optional[models.Notebook]: The notebook object if found, otherwise None.
    """
    stmt = select(models.Notebook).where(models.Notebook.title == title)
    return db.execute(stmt).scalar_one_or_none()


def get_notebook_max_score_by_notebook(
    db: Session, notebook_title: str
) -> Optional[float]:
    """
    Retrieve the maximum score for a notebook based on the notebook title.

    Args:
        db (Session): The database session to use for the query.
        notebook (str): The title of the notebook to retrieve the maximum score for.

    Returns:
        Optional[float]: The maximum score for the notebook if found, otherwise None.
    """
    stmt = select(models.Notebook.max_score).where(
        models.Notebook.title == notebook_title,
    )
    return db.execute(stmt).scalar_one_or_none()


def get_token_expiry(db: Session, value: str) -> str:
    stmt = select(models.Token).where(models.Token.value == value)
    db_token = db.execute(stmt).scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    if db_token.expires < datetime.datetime.now(datetime.UTC):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Token has expired"
        )

    return db_token.expires.isoformat()
