from typing import Optional

from pydantic import BaseModel


class Student(BaseModel):
    email: str
    given_name: str
    family_name: str
    lecture_section: Optional[int]
    lab_section: Optional[int]

    class Config:
        from_attributes = True
