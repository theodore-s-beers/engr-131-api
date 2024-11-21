from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .live_scorer import Score


class Assignment(BaseModel):
    title: str
    description: Optional[str] = None
    max_score: int
    due_date: datetime


class ScoredSubmission(BaseModel):
    student_email: str
    assignment: str
    question: str
    timestamp: datetime
    max_points: int
    points_earned: int


class ScoringSubmission(BaseModel):
    student_email: str
    term: str
    assignment: str
    question: str
    responses: dict


class QuestionSubmission(BaseModel):
    student_email: str
    term: str
    assignment: str
    question: str
    responses: dict
    score: Score


class Student(BaseModel):
    email: str
    family_name: str
    given_name: str
    lecture_section: Optional[int] = None
    lab_section: Optional[int] = None
