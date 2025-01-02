import base64
import datetime
import os
from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, HTTPException, Query, Request, UploadFile, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from nacl.public import Box, PrivateKey, PublicKey
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import crud_admin, crud_student, schemas
from .auth import verify_admin, verify_student
from .db import SessionLocal
from .live_scorer import Score, calculate_score
from .models import Token
from .question import valid_submission

from pykubegrader.log_parser.parse import LogParser
from pykubegrader.validate import read_logfile

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

#TODO: Not working yet
@app.post("/upload-score")
async def upload_score(
    cred: Credentials,
    submission: schemas.FullSubmission,
    log_file: UploadFile = File(...)
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
    verify_student(cred)  # Verify the student's credentials
    
    box = get_keybox()
    
    out, b = read_logfile(
    "/home/jca92/ENGR131_W25_dev/testing/output-testing/.output_reduced.log"
        )
    
    # print(out)

    # # Save the uploaded log file to disk (optional)
    # log_file_path = f"uploaded_{log_file.filename}"
    
    

    # print(f"Received file: {log_file.filename}")
    # print(submission.scores)
    #{"message": f"File {log_file.filename} received and processed."}
    return {"message": f"File {out} received and processed."}

def get_keybox():
    """
    Generate a public/private keypair for use with NaCl.

    Returns:
        tuple[PublicKey, PrivateKey]: A tuple containing the public and private keys.
    """
    SERVER_PRIVATE_KEY_B64 = os.getenv("SERVER_PRIVATE_KEY")
    CLIENT_PUBLIC_KEY_B64 = os.getenv("CLIENT_PUBLIC_KEY")

    if not SERVER_PRIVATE_KEY_B64 or not CLIENT_PUBLIC_KEY_B64:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server or client key not found",
        )

    SERVER_PRIVATE_KEY = PrivateKey(base64.b64decode(SERVER_PRIVATE_KEY_B64))
    CLIENT_PUBLIC_KEY = PublicKey(base64.b64decode(CLIENT_PUBLIC_KEY_B64))
    box = Box(SERVER_PRIVATE_KEY, CLIENT_PUBLIC_KEY)
    
    return box

# TODO: Complete implementation
@app.post("/validate-log-decryption")
async def validate_log_decryption(cred: Credentials, log_file: UploadFile):
    """
    Endpoint for validating the decryption of a log file.

    Returns:
        str: A message indicating that the log file was successfully decrypted.
    """
    verify_student(cred)

    box = get_keybox()

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

@app.get("/assignments", response_model=list[schemas.Assignment])
async def get_all_assignments(
    cred: Credentials, db: Session = Depends(get_db)
):
    verify_admin(cred)
    
    return crud_admin.get_assignments(db=db)


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
async def create_token(
    cred: Credentials, token_req: schemas.TokenRequest, db: Session = Depends(get_db)
):
    verify_admin(cred)

    existing_token = crud_admin.get_token_by_value(db=db, value=token_req.value)
    if existing_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token value already used",
        )

    return crud_admin.create_token(db=db, token_req=token_req)


# TODO: Implement
# @app.get("/assignment/{title}", response_model=schemas.Assignment)


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
