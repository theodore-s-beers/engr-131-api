from pydantic import BaseModel


class Student(BaseModel):
    email: str
    given_name: str
    family_name: str

    class Config:
        orm_mode = True
