from sqlalchemy.orm import Session

from . import models, schemas


def add_student(db: Session, student: schemas.Student):
    db_student = models.Student(
        email=student.email,
        family_name=student.family_name,
        given_name=student.given_name,
        lecture_section=student.lecture_section or None,
        lab_section=student.lab_section or None,
    )

    db.add(db_student)
    db.commit()
    db.refresh(db_student)

    return db_student


def get_students(db: Session, skip: int = 0, limit: int = 100):
    return (
        db.query(models.Student)
        .order_by(models.Student.family_name)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()


def delete_student_by_email(db: Session, email: str):
    db_student = db.query(models.Student).filter(models.Student.email == email).first()

    if not db_student:
        return None

    db.delete(db_student)
    db.commit()

    return db_student
