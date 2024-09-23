import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

#
# Students
#


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    given_name: Mapped[str]
    family_name: Mapped[str]
    lecture_section: Mapped[Optional[int]] = mapped_column(index=True)
    lab_section: Mapped[Optional[int]] = mapped_column(index=True)

    assignment_subs = relationship("AssignmentSubmission", back_populates="submitter")
    exam_subs = relationship("ExamSubmission", back_populates="submitter")


#
# Assignments
#


class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True, unique=True)
    description: Mapped[Optional[str]]
    max_score: Mapped[int]
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_email: Mapped[str] = mapped_column(ForeignKey("students.email"))
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    score: Mapped[int]

    submitter = relationship("Student", back_populates="assignment_subs")


#
# Exams
#


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True, unique=True)
    description: Mapped[Optional[str]]
    max_score: Mapped[int]
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ExamSubmission(Base):
    __tablename__ = "exam_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_email: Mapped[str] = mapped_column(ForeignKey("students.email"))
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    score: Mapped[int]

    submitter = relationship("Student", back_populates="exam_subs")


#
# Logins
#


class Role(enum.Enum):
    ADMIN = "admin"
    STUDENT = "student"


class Login(Base):
    __tablename__ = "logins"

    id: Mapped[int] = mapped_column(primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    role: Mapped[Role]
    ip_address: Mapped[str]
    student_email: Mapped[Optional[str]] = mapped_column(ForeignKey("students.email"))
