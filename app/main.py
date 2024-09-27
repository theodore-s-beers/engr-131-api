from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.orm import Session

from . import crud_admin, schemas
from .auth import verify_admin, verify_student
from .db import SessionLocal

app = FastAPI()

security = HTTPBasic()
Credentials: TypeAlias = Annotated[HTTPBasicCredentials, Depends(security)]


# DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#
# Student-accessible endpoints
#


@app.get("/")
async def root():
    return "Server is running"


@app.post("/login")
async def login(cred: Credentials):
    try:
        verify_admin(cred)  # Raises HTTPException (401) on failure
        return "Admin credentials verified"
    except HTTPException:
        pass

    verify_student(cred)  # Raises HTTPException (401) on failure
    return "Student credentials verified"


@app.post("/live-scorer")
async def live_scorer(req: Request, cred: Credentials):
    verify_student(cred)  # Raises HTTPException (401) on failure

    # This is just for debugging purposes
    body = await req.body()
    print(len(body.decode("utf-8")))

    return "Live-scoring request received"


@app.post("/upload-score")
async def upload_score(req: Request, cred: Credentials):
    verify_student(cred)  # Raises HTTPException (401) on failure

    # This is just for debugging purposes
    body = await req.body()
    print(len(body.decode("utf-8")))

    return "Score-upload request received"


#
# Admin-only endpoints
#


@app.post("/students", response_model=schemas.Student)
async def add_student(
    cred: Credentials,
    student: schemas.Student,
    db: Session = Depends(get_db),
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    existing_entry = crud_admin.get_student_by_email(db=db, email=student.email)
    if existing_entry:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    return crud_admin.add_student(db=db, student=student)


@app.get("/students", response_model=list[schemas.Student])
async def get_all_students(
    cred: Credentials,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    return crud_admin.get_all_students(db=db, skip=skip, limit=limit)


@app.get("/students/{email}", response_model=schemas.Student)
async def get_student_by_email(
    cred: Credentials,
    email: str,
    db: Session = Depends(get_db),
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
    verify_admin(cred)

    # Raises HTTPException (400) if emails don't match
    db_student = crud_admin.update_student(db=db, email=email, student=student)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return db_student


@app.delete("/students/{email}", response_model=schemas.Student)
async def delete_student_by_email(
    cred: Credentials,
    email: str,
    db: Session = Depends(get_db),
):
    verify_admin(cred)  # Raises HTTPException (401) on failure

    db_student = crud_admin.delete_student_by_email(db=db, email=email)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found",
        )

    return db_student
