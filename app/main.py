import datetime
import random
import tempfile
import textwrap
from typing import Annotated, Any, List, Optional, TypeAlias

from dateutil import parser as date_parser
from fastapi import (
    Depends,
    FastAPI,
    File,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pykubegrader.log_parser.parse import LogParser  # type: ignore
from pykubegrader.validate import read_logfile  # type: ignore
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import crud_admin, crud_student, schemas
from .auth import verify_admin, verify_student, verify_ta_user
from .db import SessionLocal
from .live_scorer import Score, calculate_score
from .models import Token
from .question import valid_submission
from .utils import MOTIVATIONAL_NOTES, get_key_box

app = FastAPI()

security = HTTPBasic()
Credentials: TypeAlias = Annotated[HTTPBasicCredentials, Depends(security)]


# Dependency for obtaining a database session
def get_db():
    """
    Yields a database session for use in route handlers.

    Closes the session automatically after the request is handled.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# Globally accessible endpoints
# -----------------------------


@app.get("/")
async def root(req: Request, jhub_user: str = Query(None)):
    client_host = getattr(req.client, "host", "unknown")

    response = {
        "message": "Server is running",
        "client_ip": req.headers.get("x-real-ip", client_host),
    }

    if jhub_user:
        response["jhub_user"] = jhub_user

    return response


# ----------------------------
# Student-accessible endpoints
# ----------------------------


@app.post("/live-scorer")
async def live_scorer(
    cred: Credentials, req: schemas.ScoringSubmission, db: Session = Depends(get_db)
):
    """
    Endpoint for scoring a student's live submission.

    Args:
        cred (Credentials): Basic authentication credentials for the student.
        req (schemas.ScoringSubmission): The submission details including responses.
        db (Session): Database session dependency.

    Returns:
        Score: A score object with max_points and points_earned.
    """
    verify_student(cred)

    existing_student = crud_admin.get_student_by_email(db=db, email=req.student_email)
    if not existing_student:
        new_student = schemas.Student(email=req.student_email)
        crud_admin.add_student(db=db, student=new_student)

    result = calculate_score(
        term=req.term,
        week=req.week,
        assignment=req.assignment,
        question=req.question,
        responses=req.responses,
    )

    if isinstance(result, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result,
        )

    # For the time being, allow this to fail silently
    # TODO: Revisit, fix logic...
    try:
        result_max = sum([score[1] for score in result.values()])
        result_earned = sum([score[0] for score in result.values()])
        score_for_db = Score(max_points=result_max, points_earned=result_earned)

        crud_student.add_scoring_submission(
            db=db,
            submission=req,
            score=score_for_db,
        )
    except HTTPException:
        pass

    return result


@app.post("/login")
async def login(cred: Credentials):
    """
    Endpoint for logging in as an admin or student.

    Args:
        cred (Credentials): Basic authentication credentials.

    Returns:
        str: A message indicating whether the credentials are valid for an admin or student.
    """
    try:
        verify_admin(cred)  # Raises HTTPException (401) on failure
        return "Admin credentials verified"
    except HTTPException:
        pass

    verify_student(cred)  # Raises HTTPException (401) on failure
    return "Student credentials verified"


@app.post("/score-assignment")
async def score_assignment(
    cred: Credentials,
    assignment_title: str,
    notebook_title: str,
    db: Session = Depends(get_db),
    log_file: UploadFile = File(...),
):
    """
    Endpoint for uploading a student's score along with a log file.

    Args:
        cred (Credentials): Basic authentication credentials for the student.
        submission (schemas.FullSubmission): The full submission details.
        log_file (UploadFile): The log file being uploaded.

    Returns:
        str: A message indicating that the file and submission were received.
    """
    # Validate the student's credentials
    verify_student(cred)  # Verify the student's credentials

    # Get the public/private keypair for decryption
    key_box = get_key_box()

    # reads and decrypts the log file
    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
        temp_file.write(await log_file.read())
        temp_file.flush()

        # decrypt the log file
        out, b = read_logfile(temp_file.name, key_box)

    # Parse the log file
    parser = LogParser(log_lines=out, week_tag=assignment_title)
    parser.parse_logs()
    parser.calculate_total_scores()
    results = parser.get_results()

    # extract the week number, assignment type, and submission time from the log file
    week_number: Optional[int] = results["week_num"]  # type: ignore
    assignment_type: Optional[str] = results["assignment_type"]  # type: ignore
    submission_time: str = results["student_information"]["timestamp"]
    notebook_score: float = results["assignment_information"][notebook_title][
        "total_score"
    ]

    if not week_number or not assignment_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Week number or assignment type not found",
        )

    max_score_db, due_date_db = (
        crud_student.get_max_score_and_due_date_by_week_and_type(
            db=db, week_number=week_number, assignment_type=assignment_type
        )
    )

    if not max_score_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Max score not found",
        )

    if not due_date_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Due date not found",
        )

    max_score_notebook = crud_student.get_notebook_max_score_by_notebook(
        db=db,
        notebook_title=notebook_title,
    )

    if not max_score_notebook:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Max score for notebook not found",
        )

    time_delta = crud_student.calculate_time_delta_in_seconds(
        submission_time,
        due_date_db,
    )

    grade_modifier = crud_student.get_modified_grade_percentage(time_delta)

    assignment_info: dict[str, dict[str, Any]] = results["assignment_information"]
    total_score = 0.0
    for info in assignment_info.values():
        next_score: float = info["total_score"]
        total_score += next_score

    student_email = results["student_information"]["username"]

    modified_grade = total_score / max_score_db * grade_modifier / 100

    # checks the student database for their best score, and returns their current best score.
    current_best_db = crud_student.get_best_score(
        db=db, student_email=student_email, assignment=assignment_title
    )

    current_best = None

    if current_best_db is not None:
        current_best = float(current_best_db.current_max_score)

    if current_best is None or modified_grade > current_best:
        current_best = modified_grade

    # adds the score for the assignment to the database
    crud_student.add_submitted_assignment_score(
        db=db,
        submission=schemas.AssignmentSubmission(
            student_email=student_email,
            assignment=assignment_title,
            week_number=week_number,
            assignment_type=assignment_type,
            timestamp=date_parser.parse(submission_time),
            student_seed=results["student_information"]["student_id"],
            due_date=due_date_db,
            raw_score=total_score,
            late_assignment_percentage=grade_modifier,
            submitted_score=modified_grade,
            current_max_score=current_best,
        ),
    )

    # Function to format sections for printing
    def format_section(title, content, width=70):
        wrapped_content = textwrap.fill(content, width)
        return f"{title}\n{'=' * len(title)}\n{wrapped_content}\n"

    # Start building the message
    build_message = ""

    # Add the congratulatory header
    build_message += format_section(
        "🎉 Congratulations! 🎉",
        f"{student_email}, you've successfully submitted your assignment for Week {week_number} - {assignment_type}! 🚀\n\n",
    )

    # Add raw score and status
    build_message += format_section(
        "\n📊 Raw Score",
        f"Your raw score is {notebook_score}/{max_score_notebook}. -- on this assignment you have earned {total_score}/{max_score_db} points\n\n",
    )

    if time_delta < 0:
        build_message += format_section(
            "\n✅ Submission Status",
            "On time! You've received full credit—Great Job! 🥳👏\n\n",
        )
    else:
        build_message += format_section(
            "\n⚠️ Submission Status",
            f"Late by {time_delta} seconds. Your grade has been adjusted by {grade_modifier:.2f}% of the points earned.\n\n",
        )

    # Calculate percentage score
    percentage_score = 100 * notebook_score / max_score_notebook
    build_message += format_section(
        "\n🎯 Percentage Score",
        f"Your percentage score for this notebook is {percentage_score:.2f}%.\n\n",
    )

    # Define a list of perfect messages
    perfect_messages = [
        "🌟 Fantastic work! You're mastering this material like a pro!",
        "🌠 Incredible! Your performance is shining like a star!",
        "🏆 Amazing effort! You're at the top of your game!",
        "👏 Outstanding! You're demonstrating excellent mastery!",
        "🥇 Exceptional work! You're setting a gold standard!",
        "🚀 You're crushing it! Keep up the incredible momentum!",
        "🌟 Phenomenal! Your hard work is clearly paying off!",
        "🎉 Bravo! You're making this look easy!",
        "🌈 Superb performance! You should be very proud of yourself!",
        "🎸 You're a rockstar! Keep dazzling us with your brilliance!",
    ]

    # Add motivational messages based on the score
    selected_message = random.choice(perfect_messages)
    if percentage_score >= 100:
        build_message += format_section("\n🎉 Special Note", selected_message)
    elif percentage_score >= 90:
        build_message += format_section(
            "🌟 Motivation",
            "Fantastic work! You're mastering this material like a pro! Keep it up! 💯",
        )
    elif 80 <= percentage_score < 90:
        build_message += format_section(
            "💪 Motivation",
            "Great effort! You're doing really well—keep pushing for that next level! You’ve got this! 🚀",
        )
    elif 70 <= percentage_score < 80:
        build_message += format_section(
            "👍 Motivation",
            "Good job! You're building a strong foundation—steady progress leads to mastery! 🌱",
        )
    elif 60 <= percentage_score < 70:
        build_message += format_section(
            "🌱 Motivation",
            "Keep going! You're on the right track—stay focused, and you'll keep improving! 💡",
        )
    else:
        build_message += format_section(
            "🚀 Motivation",
            "Don't be discouraged! Every step counts, and you're on the path to improvement. You’ve got this! 🌟",
        )

    # Include detailed grade information
    build_message += format_section(
        "\n📝 Submission Grade",
        f"Your grade for this submission is {modified_grade*100:.2f}%.\n\n",
    )
    build_message += format_section(
        "\n⭐ Best Score",
        f"Your current best score for this assignment is {100*current_best:.2f}%.\n\n",
    )

    # Add note about late deductions if applicable
    if time_delta > 0:
        build_message += format_section(
            "\n⏳ Late Submission Note",
            "This score includes deductions for late submission. Aim for on-time submissions to maximize your grade! 🕒\n\n",
        )

    # Randomly select one motivational note
    final_note = random.choice(MOTIVATIONAL_NOTES)

    # Add it to the final motivational send-off
    build_message += format_section("\n✨ Final Note", final_note)

    return {"message": f"{build_message}"}


@app.post("/submit-question")
async def submit_question(
    cred: Credentials, req: schemas.QuestionSubmission, db: Session = Depends(get_db)
):
    """
    Endpoint for submitting question responses and scores.

    Args:
        cred (Credentials): Basic authentication credentials for the student.
        req (schemas.QuestionSubmission): The question submission details.
        db (Session): Database session dependency.

    Returns:
        str: A message indicating successful submission to the database.
    """
    verify_student(cred)

    existing_student = crud_admin.get_student_by_email(db=db, email=req.student_email)
    if not existing_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student registration not found",
        )

    validity = valid_submission(
        term=req.term,
        assignment=req.assignment,
        question=req.question,
        responses=req.responses,
        score=req.score,
    )

    if isinstance(validity, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validity,
        )

    # Raises HTTPException (500) if assignment not in database
    _db_submission = crud_student.add_question_submission(
        db=db,
        submission=req,
    )

    return "Question responses and score saved to database"


# TODO: Complete implementation
@app.post("/validate-log-decryption")
async def validate_log_decryption(cred: Credentials, log_file: UploadFile):
    """
    Endpoint for validating the decryption of a log file.

    Returns:
        str: A message indicating that the log file was successfully decrypted.
    """
    verify_student(cred)

    box = get_key_box()

    try:
        encrypted_data = await log_file.read()

        decrypted_data = box.decrypt(encrypted_data)

        print(len(decrypted_data.splitlines()))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to decrypt log file: {e}",
        )

    return "Log file successfully decrypted"


@app.get("/validate-token/{token_value}")
async def validate_token(
    cred: Credentials, token_value: str, db: Session = Depends(get_db)
):
    """
    Validate if a token exists and is not expired.

    Args:
        token_value (str): The value of the token to validate.
        db (Session): Database session dependency.

    Returns:
        dict: Validation result.

    Raises:
        HTTPException: If the token does not exist or is expired.
    """
    verify_student(cred)

    stmt = select(Token).where(Token.value == token_value)
    token = db.execute(stmt).scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Token not found"
        )

    # TODO: Return 200 in this case, with a message indicating the token is expired
    if token.expires < datetime.datetime.now(datetime.UTC):
        raise HTTPException(
            status_code=status.HTTP_418_IM_A_TEAPOT, detail="Token has expired"
        )

    return {"status": "valid", "expires_at": token.expires.isoformat()}


# ----------------------
# Admin-only endpoints
# ----------------------


@app.post("/notebook", response_model=schemas.Notebook)
async def add_notebook(
    cred: Credentials, notebook: schemas.Notebook, db: Session = Depends(get_db)
):
    verify_admin(cred)

    existing_notebook = crud_admin.get_notebook_by_title(db=db, title=notebook.title)

    if existing_notebook:
        # Update existing notebook
        updated_notebook = crud_admin.update_notebook(
            db=db, title=notebook.title, notebook=notebook
        )
        if updated_notebook:
            return updated_notebook

    # Create a new notebook
    return crud_admin.add_notebook(db=db, notebook=notebook)


@app.post("/assignments", response_model=schemas.Assignment)
async def add_assignment(
    cred: Credentials, assignment: schemas.Assignment, db: Session = Depends(get_db)
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    existing_assignment = crud_admin.get_assignment_by_title(
        db=db, title=assignment.title
    )

    if existing_assignment:
        # Update existing assignment
        updated_assignment = crud_admin.update_assignment(
            db=db, title=assignment.title, assignment=assignment
        )
        if updated_assignment:
            return updated_assignment

    # Create a new assignment
    return crud_admin.add_assignment(db=db, assignment=assignment)


@app.post("/students", response_model=schemas.Student)
async def add_student(
    cred: Credentials, student: schemas.Student, db: Session = Depends(get_db)
):
    """
    Endpoint for adding a new student to the database.

    Args:
        cred (Credentials): Basic authentication credentials for the admin.
        student (schemas.Student): The student details.
        db (Session): Database session dependency.

    Returns:
        schemas.Student: The newly created student object.
    """
    verify_admin(cred)  # Raises HTTPException (401) on failure

    existing_entry = crud_admin.get_student_by_email(db=db, email=student.email)
    if existing_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return crud_admin.add_student(db=db, student=student)


@app.post("/tokens", response_model=schemas.Token)
async def create_token(token: schemas.TokenRequest, db: Session = Depends(get_db)):
    # This endpoint is accessible to instructors and TAs
    verify_ta_user(username=token.requester)

    existing_token = crud_admin.get_token_by_value(db=db, value=token.value)
    if existing_token:
        updated_token = crud_admin.update_token(db=db, token=token)
        if updated_token:
            return updated_token

    return crud_admin.create_token(db=db, token_req=token)


@app.get("/assignment-grades", response_model=List[schemas.AssignmentSubmission])
async def get_assignment_grades(
    cred: Credentials,
    db: Session = Depends(get_db),
    assignment_type: str = Query(..., description="Type of assignment"),
    week_number: int = Query(..., description="Week number for the assignment"),
):
    """
    Retrieve assignment grades filtered by assignment type and week number.

    Args:
        cred (dict): Verified admin credentials.
        db (Session): Database session.
        assignment_type (str): Type of the assignment.
        week_number (int): Week number for filtering grades.

    Returns:
        List[AssignmentSubmission]: List of assignment grades.
    """
    verify_admin(cred)  # Raises HTTPException (401) on failure

    return crud_admin.get_assignment_grades(
        db=db, assignment_type=assignment_type, week_number=week_number
    )


@app.get("/assignments", response_model=list[schemas.Assignment])
async def get_all_assignments(cred: Credentials, db: Session = Depends(get_db)):
    verify_admin(cred)

    return crud_admin.get_assignments(db=db)


@app.get("/notebooks", response_model=list[schemas.Notebook])
async def get_all_notebooks(cred: Credentials, db: Session = Depends(get_db)):
    verify_admin(cred)

    return crud_admin.get_notebooks(db=db)


@app.get("/scoring/{email}", response_model=list[schemas.ScoredSubmission])
async def get_scoring_subs_by_email(
    cred: Credentials, email: str, db: Session = Depends(get_db)
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    return crud_admin.get_scoring_subs_by_email(db=db, email=email)


@app.get("/students", response_model=list[schemas.Student])
async def get_all_students(
    cred: Credentials, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    return crud_admin.get_all_students(db=db, skip=skip, limit=limit)


@app.get("/students/{email}", response_model=schemas.Student)
async def get_student_by_email(
    cred: Credentials, email: str, db: Session = Depends(get_db)
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    db_student = crud_admin.get_student_by_email(db=db, email=email)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return db_student


@app.put("/assignments/{title}", response_model=schemas.Assignment)
async def update_assignment(
    cred: Credentials,
    title: str,
    assignment: schemas.Assignment,
    db: Session = Depends(get_db),
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    db_assignment = crud_admin.update_assignment(
        db=db, title=title, assignment=assignment
    )

    return db_assignment


@app.put("/students/{email}", response_model=schemas.Student)
async def update_student(
    cred: Credentials,
    email: str,
    student: schemas.Student,
    db: Session = Depends(get_db),
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    # The email address in the path is used to identify the record to update. If
    # student.email is different, the record will be updated with that address, unless
    # it is already in use -- in which case an HTTPException (400) is raised.
    db_student = crud_admin.update_student(db=db, email=email, student=student)

    # i.e., if no record was found with the email address in the path
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return db_student


@app.delete("/students/{email}", response_model=schemas.Student)
async def delete_student_by_email(
    cred: Credentials, email: str, db: Session = Depends(get_db)
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    db_student = crud_admin.delete_student_by_email(db=db, email=email)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return db_student
