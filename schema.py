from typing import Optional, List
from pydantic import BaseModel


class StudentSchema(BaseModel):
    # id: Optional[int] = None
    name: str

    class Config:
        orm_mode = True


class StudentUpdateSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class SubjectSchema(BaseModel):
    name: str

    class Config:
        orm_mode = True


class SubjectUpdateSchema(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class MarksSchema(BaseModel):
    student_id: int
    subject_id: int
    marks: int

    class Config:
        orm_mode = True


class MarksUpdateSchema(BaseModel):
    id: int
    student_id: int
    subject_id: int
    marks: int

    class Config:
        orm_mode = True


class FetchMarksSchema(BaseModel):
    subject_id: int
    subject_name: str
    marks: int

    class Config:
        orm_mode = True


class FetchStudentSchema(BaseModel):
    student_id: int
    student_name: str
    details: List[FetchMarksSchema] = []

    class Config:
        orm_mode = True


class FetchAllStudentsSchema(BaseModel):
    students: List[FetchStudentSchema] = []

    class Config:
        orm_mode = True
