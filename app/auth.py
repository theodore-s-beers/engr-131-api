import os

import bcrypt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials

load_dotenv()

adm_pw_env = os.getenv("ADMIN_PASSWORD") or ""
adm_pw = bcrypt.hashpw(adm_pw_env.encode(), bcrypt.gensalt())

stud_pw_env = os.getenv("STUDENT_PASSWORD") or ""
stud_pw = bcrypt.hashpw(stud_pw_env.encode(), bcrypt.gensalt())


def auth_exception():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def verify_admin(cr: HTTPBasicCredentials):
    if cr.username != "admin" or not bcrypt.checkpw(cr.password.encode(), adm_pw):
        raise auth_exception()


def verify_student(cr: HTTPBasicCredentials):
    if cr.username != "student" or not bcrypt.checkpw(cr.password.encode(), stud_pw):
        raise auth_exception()
