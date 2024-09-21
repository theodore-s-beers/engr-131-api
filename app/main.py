from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .auth import verify_admin, verify_student

app = FastAPI()

security = HTTPBasic()
Credentials: TypeAlias = Annotated[HTTPBasicCredentials, Depends(security)]


@app.get("/")
async def root():
    return "Hello world"


@app.post("/login")
async def login(cr: Credentials):
    try:
        verify_admin(cr)  # Raises HTTPException on failure
        return Response(status_code=status.HTTP_200_OK)
    except HTTPException:
        pass

    verify_student(cr)  # Raises HTTPException on failure
    return Response(status_code=status.HTTP_200_OK)


@app.post("/live-scorer")
async def live_scorer(req: Request, cr: Credentials):
    verify_student(cr)  # Raises HTTPException on failure

    body = await req.body()
    print(len(body.decode("utf-8")))

    return "Live-scoring request received"


@app.post("/upload-score")
async def upload_score(req: Request, cr: Credentials):
    verify_student(cr)  # Raises HTTPException on failure

    body = await req.body()
    print(len(body.decode("utf-8")))

    return "Score-upload request received"
