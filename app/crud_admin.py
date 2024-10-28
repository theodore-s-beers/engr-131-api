from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas

#
# Students table
#


def add_student(db: Session, student: schemas.Student):
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


def get_all_students(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Student)
        .order_by(models.Student.family_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()


def update_student(db: Session, email: str, student: schemas.Student):
    db_student = db.query(models.Student).filter(models.Student.email == email).first()
    if not db_student:
        return None

    if email != student.email:
        existing_email = (
            db.query(models.Student)
            .filter(models.Student.email == student.email)
            .first()
        )

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


def delete_student_by_email(db: Session, email: str):
    db_student = db.query(models.Student).filter(models.Student.email == email).first()

    if not db_student:
        return None

    db.delete(db_student)
    db.commit()

    return db_student


#
# Assignments table
#


def add_assignment(db: Session, assignment: schemas.Assignment):
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


def get_assignment_by_title(db: Session, title: str):
    return db.query(models.Assignment).filter(models.Assignment.title == title).first()
