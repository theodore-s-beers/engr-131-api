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

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Sequence

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound


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
        week_number=assignment.week_number,
        assignment_type=assignment.assignment_type,
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found",
        )

    db_assignment.title = assignment.title
    db_assignment.description = assignment.description
    db_assignment.max_score = assignment.max_score
    db_assignment.due_date = assignment.due_date
    db_assignment.week_number = assignment.week_number
    db_assignment.assignment_type = assignment.assignment_type

    db.commit()
    db.refresh(db_assignment)

    return db_assignment


#
# Notebooks table
#


def add_notebook(db: Session, notebook: schemas.Notebook) -> models.Notebook:
    """
    Add a new notebook to the database.

    Args:
        db (Session): The database session to use for the operation.
        notebook (schemas.Notebook): The notebook data to be added.

    Returns:
        models.Notebook: The newly created notebook object.
    """
    db_notebook = models.Notebook(
        title=notebook.title,
        week_number=notebook.week_number,
        assignment_type=notebook.assignment_type,
        max_score=notebook.max_score,
        due_date=notebook.due_date,
    )

    db.add(db_notebook)
    db.commit()
    db.refresh(db_notebook)

    return db_notebook


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


def get_notebooks(db: Session) -> Sequence[models.Notebook]:
    """
    Retrieve all notebooks from the database.

    Args:
        db (Session): The database session to use for the query.

    Returns:
        Sequence[models.Notebook]: A sequence of Notebook objects.
    """
    stmt = select(models.Notebook)
    return db.execute(stmt).scalars().all()


def update_notebook(
    db: Session, title: str, notebook: schemas.Notebook
) -> models.Notebook:
    """
    Adds a new notebook to the database.

    Args:
        db (Session): The database session to use for the operation.
        notebook (schemas.Notebook): The notebook data to be added

    Returns:
        models.Notebook: The newly created notebook object.
    """
    stmt = select(models.Notebook).where(models.Notebook.title == title)
    db_notebook = db.execute(stmt).scalar_one_or_none()

    if not db_notebook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notebook not found",
        )

    db_notebook.title = notebook.title
    db_notebook.week_number = notebook.week_number
    db_notebook.assignment_type = notebook.assignment_type
    db_notebook.max_score = notebook.max_score
    db_notebook.due_date = notebook.due_date

    db.commit()
    db.refresh(db_notebook)

    return db_notebook


#
# Scoring submissions table
#


def get_scoring_subs_by_email(
    db: Session, email: str
) -> Sequence[models.AssignmentSubmission]:
    """
    Retrieve scoring submissions by student email.

    Args:
        db (Session): The database session to use for the query.
        email (str): The email address of the student.

    Returns:
        Sequence[models.AssignmentSubmission]: A sequence of ScoringSubmission objects
        associated with the given email, ordered by timestamp in descending order.
    """
    # Validate the email
    if not email:
        raise ValueError("Email must be provided and cannot be empty.")
    
    # Query the database
    stmt = (
        select(models.AssignmentSubmission).where(
            models.AssignmentSubmission.student_email == email.split('@')[0])#.order_by(
            # models.AssignmentSubmission.timestamp.desc())
    )

    try:
        results = db.execute(stmt).scalar()#.all()
        if not results:
            raise NoResultFound(f"No submissions found for email: {email}")
        return results
    except Exception as e:
        raise RuntimeError(f"An error occurred while fetching submissions: {e}")
    


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
        requester=token_req.requester,
    )

    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


def get_all_tokens(db: Session) -> Sequence[models.Token]:
    """
    Retrieve all tokens from the database

    Args:
        db (Session): The database session to use for the query

    Returns:
        Sequence[models.Token]: A sequence of Token objects
    """
    stmt = select(models.Token)
    return db.execute(stmt).scalars().all()


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


# TODO: Add a way to track history of all tokens
def update_token(db: Session, token: schemas.TokenRequest):
    stmt = select(models.Token).where(models.Token.value == token.value)
    db_token = db.execute(stmt).scalar_one_or_none()

    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found",
        )

    db_token.value = token.value
    db_token.created = datetime.now()
    db_token.expires = db_token.created + timedelta(minutes=token.duration)
    db_token.requester = token.requester

    db.commit()
    db.refresh(db_token)

    return db_token


#
# Grades table
#


def find_best_submission_id(db: Session, student_email: str, assignment: str) -> int:
    # Given student email and assignment name, find the ID (sic) of the
    # submission with the highest submitted_score value
    # TODO: Consider choosing the submission with the highest raw_score instead
    stmt = (
        select(models.AssignmentSubmission.id)
        .where(
            models.AssignmentSubmission.student_email == student_email,
            models.AssignmentSubmission.assignment == assignment,
        )
        .order_by(models.AssignmentSubmission.submitted_score.desc())
    )
    result = db.execute(stmt).scalar_one_or_none()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No submissions found for the provided student and assignment",
        )

    return result


def get_all_assignment_subs(db: Session) -> Sequence[models.AssignmentSubmission]:
    stmt = select(models.AssignmentSubmission)
    return db.execute(stmt).scalars().all()


def get_all_submission_emails(db: Session) -> List[str]:
    stmt = select(models.AssignmentSubmission.student_email).distinct()
    return [row.student_email for row in db.execute(stmt).all()]


def get_assignment_grades(
    db: Session,
    week_number: int,
    assignment_type: str,
) -> List[Dict[str, float]]:
    """
    Retrieve the best max score for each unique student for a given week number and assignment.

    Args:
        db (Session): The database session to use for the query.
        week_number (int): The week number to filter submissions.
        assignment (str): The assignment name to filter submissions.

    Returns:
        List[Dict[str, float]]: A list of dictionaries containing student email and their best score.
    """
    stmt = (
        select(
            models.AssignmentSubmission.student_email,
            func.max(models.AssignmentSubmission.current_max_score).label("best_score"),
        )
        .where(
            models.AssignmentSubmission.week_number == week_number,
            models.AssignmentSubmission.assignment == assignment_type,
        )
        .group_by(models.AssignmentSubmission.student_email)
    )

    result = db.execute(stmt).all()

    # Convert the result into a list of dictionaries
    return [
        {"student_email": row.student_email, "best_score": row.best_score}
        for row in result
    ]


def get_grades_testing(db: Session):
    student_submission_map = {}

    assignments = get_assignments(db)

    for assignment in assignments:
        all_relevant_submissions_stmt = select(models.AssignmentSubmission).where(
            models.AssignmentSubmission.assignment == assignment.title,
            models.AssignmentSubmission.week_number == assignment.week_number,
        )
        all_relevant_submissions = (
            db.execute(all_relevant_submissions_stmt).scalars().all()
        )

        for submission in all_relevant_submissions:
            if submission.student_email not in student_submission_map:
                student_submission_map[submission.student_email] = submission
                continue

            for i, student_submission in enumerate(
                student_submission_map[submission.student_email]
            ):
                if (
                    student_submission.assignment == submission.assignment
                    and student_submission.current_max_score
                    < submission.current_max_score
                ):
                    student_submission_map[submission.student_email][i] = submission
                    break
            else:
                student_submission_map[submission.student_email].append(submission)

    return student_submission_map


def get_student_grades(db: Session) -> list[schemas.StudentGrades]:
    """
    Retrieve student grades as a list of dictionaries.

    :param db: SQLAlchemy session
    :return: A list of dicts containing student emails and their best assignment scores.
    """

    # Query the database to get the best score per assignment for each student
    stmt = (
        select(
            models.AssignmentSubmission.student_email,
            models.AssignmentSubmission.assignment,
            func.max(models.AssignmentSubmission.submitted_score).label("best_score"),
        )
        .group_by(
            models.AssignmentSubmission.student_email,
            models.AssignmentSubmission.assignment,
        )
        .order_by(models.AssignmentSubmission.student_email)
    )

    # Execute the query
    results = db.execute(stmt).tuples().all()

    # Organize results into the desired structure
    student_grades: dict[str, dict[str, Any]] = defaultdict(lambda: {"grades": {}})

    for student_email, assignment, best_score in results:
        if student_email not in student_grades:
            student_grades[student_email]["student_email"] = student_email
        percentage_score = (
            round(best_score * 100, 2) if best_score is not None else 0.00
        )
        student_grades[student_email]["grades"][assignment] = percentage_score

    # Convert to a list of dicts
    return [
        schemas.StudentGrades(
            student_email=student["student_email"], grades=student["grades"]
        )
        for student in student_grades.values()
    ]


def update_assignment_score(
    db: Session,
    submission_id: int,
    student_email: str,
    assignment: str,
    new_score: float,
) -> models.AssignmentSubmission:
    # Find the relevant submission by ID (sic)
    stmt = select(models.AssignmentSubmission).where(
        models.AssignmentSubmission.id == submission_id
    )
    db_submission = db.execute(stmt).scalar_one_or_none()

    # Raise 500 because the ID will have come from another CRUD function
    # i.e., the request itself has already been validated
    if not db_submission:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submission not found in DB",
        )

    # Again raise 500; ID was found via student email and assignment name
    if (
        db_submission.student_email != student_email
        or db_submission.assignment != assignment
    ):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Submission in DB does not match student email and assignment name",
        )

    db_submission.updated_score = new_score
    db.commit()
    db.refresh(db_submission)

    return db_submission
