from pydantic import BaseModel


class Student(BaseModel):
    email: str
    given_name: str
    family_name: str

    class Config:
        from_attributes = True
