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
    stmt = (
        select(models.Student)
        .order_by(models.Student.family_name)
        .offset(skip)
        .limit(limit)
    )

    return db.execute(stmt).scalars().all()


def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    stmt = select(models.Student).where(models.Student.email == email)
    return db.execute(stmt).scalar_one_or_none()


def update_student(
    db: Session, email: str, student: schemas.Student
) -> Optional[models.Student]:
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
    stmt = select(models.Assignment).where(models.Assignment.title == title)
    return db.execute(stmt).scalar_one_or_none()


#
# Scoring submissions table
#


def get_scoring_subs_by_email(
    db: Session, email: str
) -> Sequence[models.ScoringSubmission]:
    stmt = (
        select(models.ScoringSubmission)
        .where(models.ScoringSubmission.student_email == email)
        .order_by(models.ScoringSubmission.timestamp.desc())
    )

    return db.execute(stmt).scalars().all()


#
# Other
#


def get_token_by_value(db: Session, value: str) -> Optional[models.Token]:
    stmt = select(models.Token).where(models.Token.value == value)
    return db.execute(stmt).scalar_one_or_none()


def create_token(db: Session, token_req: schemas.TokenRequest) -> models.Token:
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
