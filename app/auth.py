"""
auth.py

This module provides authentication functionalities for admin and student users.
It includes functions to verify credentials and raise appropriate HTTP exceptions
for unauthorized access.

Environment Variables:
- ADMIN_PASSWORD: The password for the admin user.
- STUDENT_PASSWORD: The password for the student user.

Dependencies:
- bcrypt: Library for hashing and checking passwords.
- fastapi: Web framework for building APIs with Python.
"""

import os

import bcrypt
from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials

adm_pw_env = os.getenv("ADMIN_PASSWORD") or ""
adm_pw = bcrypt.hashpw(adm_pw_env.encode(), bcrypt.gensalt())

stud_pw_env = os.getenv("STUDENT_PASSWORD") or ""
stud_pw = bcrypt.hashpw(stud_pw_env.encode(), bcrypt.gensalt())


def auth_exception():
    """
    Raises an HTTP 401 Unauthorized exception with a specific error message and headers.

    Raises:
        HTTPException: An exception indicating that the user is not authorized to access the resource.
    """
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Basic"},
    )


def verify_admin(cred: HTTPBasicCredentials):
    """
    Verifies if the provided credentials belong to an admin user.

    Args:
        cred (HTTPBasicCredentials): The credentials to verify, containing a username and password.

    Raises:
        auth_exception: If the credentials do not match the admin username and password.
    """
    if cred.username != "admin" or not bcrypt.checkpw(cred.password.encode(), adm_pw):
        raise auth_exception()


def verify_student(cred: HTTPBasicCredentials):
    """
    Verifies if the provided credentials match the expected student credentials.

    Args:
        cred (HTTPBasicCredentials): The credentials to verify, containing a username and password.

    Raises:
        HTTPException: If the username is not "student" or the password does not match the expected password.
    """
    if cred.username != "student" or not bcrypt.checkpw(
        cred.password.encode(), stud_pw
    ):
        raise auth_exception()
