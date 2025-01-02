"""
crud_admin.py

This module provides CRUD operations for managing students, assignments, scoring submissions,
and tokens in the database using SQLAlchemy and FastAPI.

Functions:
    add_student(db: Session, student: schemas.Student) -> models.Student
    get_all_students(db: Session, skip: int = 0, limit: int = 100) -> Sequence[models.Student]
    get_student_by_email(db: Session, email: str) -> Optional[models.Student]
    update_student(db: Session, email: str, student: schemas.Student) -> Optional[models.Student]
    delete_student_by_email(db: Session, email: str) -> Optional[models.Student]
    add_assignment(db: Session, assignment: schemas.Assignment) -> models.Assignment
    get_assignment_by_title(db: Session, title: str) -> Optional[models.Assignment]
    get_scoring_subs_by_email(db: Session, email: str) -> Sequence[models.ScoringSubmission]
    get_token_by_value(db: Session, value: str) -> Optional[models.Token]
    create_token(db: Session, token_req: schemas.TokenRequest) -> models.Token
"""

from datetime import datetime, timedelta
from typing import Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas

#
# Students table
#


def add_student(db: Session, student: schemas.Student) -> models.Student:
    """
    Add a new student to the database.

    Args:
        db (Session): The database session to use for the operation.
        student (schemas.Student): The student data to be added.

    Returns:
        models.Student: The newly added student record.
    """
    db_student = models.Student(
        email=student.email,
        family_name=student.family_name,
        given_name=student.given_name,
        lecture_section=student.lecture_section,
        lab_section=student.lab_section,
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student


def get_all_students(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[models.Student]:
    """
    Retrieve a list of students from the database, ordered by family name.

    Args:
        db (Session): The database session to use for the query.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 100.

    Returns:
        Sequence[models.Student]: A list of student records.
    """
    stmt = (
        select(models.Student)
        .order_by(models.Student.family_name)
        .offset(skip)
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()


def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    """
    Retrieve a student record from the database by email.

    Args:
        db (Session): The database session to use for the query.
        email (str): The email address of the student to retrieve.

    Returns:
        Optional[models.Student]: The student record if found, otherwise None.
    """
    stmt = select(models.Student).where(models.Student.email == email)
    return db.execute(stmt).scalar_one_or_none()


def update_student(
    db: Session, email: str, student: schemas.Student
) -> Optional[models.Student]:
    """
    Update a student's information in the database.

    Args:
        db (Session): The database session to use for the update.
        email (str): The email of the student to update.
        student (schemas.Student): The new student data to update.

    Returns:
        Optional[models.Student]: The updated student object if the update was successful,
        or None if the student with the given email was not found.

    Raises:
        HTTPException: If the new email is already registered to another student.
    """
    stmt = select(models.Student).where(models.Student.email == email)
    db_student = db.execute(stmt).scalar_one_or_none()
    if not db_student:
        return None

    if email != student.email:
        stmt = select(models.Student).where(models.Student.email == student.email)
        existing_email = db.execute(stmt).scalar_one_or_none()

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested email already registered",
            )

        db_student.email = student.email

    db_student.family_name = student.family_name
    db_student.given_name = student.given_name

    if student.lecture_section is not None:
        db_student.lecture_section = student.lecture_section

    if student.lab_section is not None:
        db_student.lab_section = student.lab_section

    db.commit()
    db.refresh(db_student)

    return db_student


def delete_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    """
    Delete a student from the database by their email.

    Args:
        db (Session): The database session to use for the operation.
        email (str): The email of the student to delete.

    Returns:
        Optional[models.Student]: The deleted student object if found and deleted, otherwise None.
    """
    stmt = select(models.Student).where(models.Student.email == email)
    db_student = db.execute(stmt).scalar_one_or_none()

    if not db_student:
        return None

    db.delete(db_student)
    db.commit()

    return db_student


#
# Assignments table
#


def add_assignment(db: Session, assignment: schemas.Assignment) -> models.Assignment:
    """
    Add a new assignment to the database.

    Args:
        db (Session): The database session to use for the operation.
        assignment (schemas.Assignment): The assignment data to be added.

    Returns:
        models.Assignment: The newly created assignment object.
    """
    db_assignment = models.Assignment(
        title=assignment.title,
        description=assignment.description,
        max_score=assignment.max_score,
        due_date=assignment.due_date,
    )

    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)

    return db_assignment


def get_assignment_by_title(db: Session, title: str) -> Optional[models.Assignment]:
    """
    Retrieve an assignment from the database by its title.

    Args:
        db (Session): The database session to use for the query.
        title (str): The title of the assignment to retrieve.

    Returns:
        Optional[models.Assignment]: The assignment object if found, otherwise None.
    """
    stmt = select(models.Assignment).where(models.Assignment.title == title)
    return db.execute(stmt).scalar_one_or_none()

def get_assignments(db: Session) -> Sequence[models.Assignment]:
    """
    Retrieve all assignments from the database.

    Args:
        db (Session): The database session to use for the query.

    Returns:
        Sequence[models.Assignment]: A sequence of Assignment objects.
    """
    stmt = select(models.Assignment)
    return db.execute(stmt).scalars().all()


#
# Scoring submissions table
#


def get_scoring_subs_by_email(
    db: Session, email: str
) -> Sequence[models.ScoringSubmission]:
    """
    Retrieve scoring submissions by student email.

    Args:
        db (Session): The database session to use for the query.
        email (str): The email address of the student.

    Returns:
        Sequence[models.ScoringSubmission]: A sequence of ScoringSubmission objects
        associated with the given email, ordered by timestamp in descending order.
    """
    stmt = (
        select(models.ScoringSubmission)
        .where(models.ScoringSubmission.student_email == email)
        .order_by(models.ScoringSubmission.timestamp.desc())
    )

    return db.execute(stmt).scalars().all()


#
# Tokens table
#


def create_token(db: Session, token_req: schemas.TokenRequest) -> models.Token:
    """
    Create a new token and store it in the database.

    Args:
        db (Session): The database session to use for the operation.
        token_req (schemas.TokenRequest): The token request containing the value and duration for the token.

    Returns:
        models.Token: The created token object with value, created, and expires fields populated.
    """
    created: datetime = datetime.now()
    expires: datetime = created + timedelta(minutes=token_req.duration)

    db_token = models.Token(
        value=token_req.value,
        created=created,
        expires=expires,
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


def get_token_by_value(db: Session, value: str) -> Optional[models.Token]:
    """
    Retrieve a token from the database by its value.

    Args:
        db (Session): The database session to use for the query.
        value (str): The value of the token to retrieve.

    Returns:
        Optional[models.Token]: The token object if found, otherwise None.
    """
    stmt = select(models.Token).where(models.Token.value == value)
    return db.execute(stmt).scalar_one_or_none()


def update_assignment(
    db: Session, title: str, assignment: schemas.Assignment
) -> models.Assignment:
    """
    Add a new assignment to the database.

    Args:
        db (Session): The database session to use for the operation.
        assignment (schemas.Assignment): The assignment data to be added.

    Returns:
        models.Assignment: The newly created assignment object.
    """

    stmt = select(models.Assignment).where(models.Assignment.title == title)
    db_assignment = db.execute(stmt).scalar_one_or_none()

    if not db_assignment:
        return None

    db_assignment.title = assignment.title
    db_assignment.description = assignment.description
    db_assignment.max_score = assignment.max_score
    db_assignment.due_date = assignment.due_date

    db.commit()
    db.refresh(db_assignment)

    return db_assignment
