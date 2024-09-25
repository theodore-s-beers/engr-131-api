from sqlalchemy.orm import Session

from . import models, schemas


def add_student(db: Session, student: schemas.Student):
    db_student = models.Student(
        email=student.email,
        given_name=student.given_name,
        family_name=student.family_name,
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student


def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()


def get_students(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Student).offset(skip).limit(limit).all()
