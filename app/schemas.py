from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from .live_scorer import Score


@dataclass
class QuestionScoreFinal:
    name: str
    score: int
    max_score: int


class Assignment(BaseModel):
    title: str
    description: Optional[str] = None
    max_score: float
    due_date: datetime
    week_number: int
    assignment_type: str


class FullSubmission(BaseModel):
    student_email: str
    assignment: str
    start_time: datetime
    end_time: datetime
    scores: list[QuestionScoreFinal]


class QuestionSubmission(BaseModel):
    student_email: str
    term: str
    assignment: str
    question: str
    responses: dict
    score: Score


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
    week: str
    assignment: str
    question: str
    responses: dict


class Student(BaseModel):
    email: str
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    lecture_section: Optional[int] = None
    lab_section: Optional[int] = None


class Token(BaseModel):
    value: str
    created: datetime
    expires: datetime
    requester: str
    student_id: Optional[str] = None
    assignment: Optional[str] = None


class TokenRequest(BaseModel):
    value: str
    duration: int = 120
    requester: str = "admin"
    student_id: Optional[str] = None
    assignment: Optional[str] = None


class Question(BaseModel):
    title: str
    assignment: str
    max_points: Optional[float] = None
    due_date: Optional[datetime] = None
    week_number: Optional[int] = None
    assignment_type: Optional[str] = None


class AssignmentSubmission(BaseModel):
    student_email: str
    assignment: str
    week_number: Optional[int]
    assignment_type: Optional[str]
    timestamp: datetime
    student_seed: int
    due_date: datetime
    raw_score: float
    late_assignment_percentage: float
    submitted_score: float
    current_max_score: float
    updated_score: Optional[float] = None
    key_used: Optional[str] = None


# This is a schema for the students_completed_assignments table
# It is used to store students who have turned in final versions of assignments
# and thus cannot submit again
class StudentsCompletedAssignments(BaseModel):
    student_email: str
    assignment: str
    week_number: Optional[int]
    assignment_type: Optional[str]
    timestamp: Optional[datetime] = None
    student_seed: Optional[int] = None
    key_used: Optional[str] = None


class Notebook(BaseModel):
    title: str
    week_number: Optional[int]
    assignment_type: Optional[str]
    due_date: datetime
    max_score: float


class NotebookSubmission(BaseModel):
    student_email: str
    notebook: str
    week_number: Optional[int]
    assignment_type: Optional[str]
    timestamp: datetime
    student_seed: int
    due_date: datetime
    raw_score: float
    late_assignment_percentage: float
    submitted_score: float
    current_max_score: float


class StudentGrades(BaseModel):
    student_email: str
    grades: dict[str, float]


class GradeUpdateRequest(BaseModel):
    student_email: str
    assignment: str
    updated_score: float


class ExecutionLogUpload(BaseModel):
    student_email: str
    assignment: str
    encrypted_content: bytes
