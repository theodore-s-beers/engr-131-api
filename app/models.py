import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

#
# Students
#


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(index=True, unique=True)
    family_name: Mapped[Optional[str]] = mapped_column()
    given_name: Mapped[Optional[str]] = mapped_column()
    lecture_section: Mapped[Optional[int]] = mapped_column(index=True)
    lab_section: Mapped[Optional[int]] = mapped_column(index=True)


#
# Assignments
#


# TODO: Grading mechanism
class Assignment(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True, unique=True)
    description: Mapped[Optional[str]]
    week_number: Mapped[Optional[int]]
    assignment_type: Mapped[Optional[str]]
    max_score: Mapped[float]
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_email: Mapped[str] 
    assignment: Mapped[str]
    week_number: Mapped[Optional[int]]
    assignment_type: Mapped[Optional[str]]
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    student_seed: Mapped[int]
    due_date: Mapped[datetime]
    raw_score: Mapped[float]
    late_assignment_percentage: Mapped[float]
    submitted_score: Mapped[float]
    current_max_score: Mapped[float]


class QuestionSubmission(Base):
    __tablename__ = "question_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_email: Mapped[str] = mapped_column(ForeignKey("students.email"))
    assignment: Mapped[str] = mapped_column(ForeignKey("assignments.title"))
    question: Mapped[str]

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    responses: Mapped[dict]
    max_points: Mapped[float]
    points_earned: Mapped[float]


class ScoringSubmission(Base):
    __tablename__ = "scoring_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_email: Mapped[str] = mapped_column(ForeignKey("students.email"))
    assignment: Mapped[str] = mapped_column(ForeignKey("assignments.title"))
    question: Mapped[str]

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    max_points: Mapped[float]
    points_earned: Mapped[float]


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


#
# Other
#


class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(index=True, unique=True)
    created: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires: Mapped[datetime] = mapped_column(DateTime(timezone=True))
