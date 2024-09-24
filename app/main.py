from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, HTTPException, Request
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
async def login(cr: Credentials):
    try:
        verify_admin(cr)  # Raises HTTPException on failure
        return "Admin credentials verified"
    except HTTPException:
        pass

    verify_student(cr)  # Raises HTTPException on failure
    return "Student credentials verified"


@app.post("/live-scorer")
async def live_scorer(req: Request, cr: Credentials):
    verify_student(cr)  # Raises HTTPException on failure

    # This is just for debugging purposes
    body = await req.body()
    print(len(body.decode("utf-8")))

    return "Live-scoring request received"


@app.post("/upload-score")
async def upload_score(req: Request, cr: Credentials):
    verify_student(cr)  # Raises HTTPException on failure

    # This is just for debugging purposes
    body = await req.body()
    print(len(body.decode("utf-8")))

    return "Score-upload request received"


#
# Admin-only endpoints
#


@app.get("/students", response_model=list[schemas.Student])
async def get_students(
    cr: Credentials,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    verify_admin(cr)
    students = crud_admin.get_students(db, skip=skip, limit=limit)
    return students


@app.post("/students", response_model=schemas.Student)
async def add_student(
    cr: Credentials,
    student: schemas.Student,
    db: Session = Depends(get_db),
):
    verify_admin(cr)
    db_student = crud_admin.get_student_by_email(db, email=student.email)
    if db_student:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud_admin.add_student(db=db, student=student)
