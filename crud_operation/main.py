import schema
import models
from database import database
from fastapi import FastAPI
from fpdf import FPDF
app = FastAPI()

app.state.database = database

@app.on_event("startup")
async def startup() -> None:
    database_ = app.state.database
    if not database_.is_connected:
        await database_.connect()


@app.on_event("shutdown")
async def shutdown() -> None:
    database_ = app.state.database
    if database_.is_connected:
        await database_.disconnect()

# Get all Students

@app.get('/all_students')
async def all_students():
    students = await models.Student.objects.all()
    return students


# Get all Subjects
@app.get('/all_subjects')
async def all_subjects():
    subjects = await models.Subject.objects.all()
    return subjects


# Get all Marks

@app.get('/all_marks')
async def all_marks():
    marks = await models.Marks.objects.all()
    return marks


# Get Student by id

@app.get('/students_by_id/{student_id}')
async def students_by_id(id: int):
    students = await models.Student.objects.get(id=id)
    return students


# Get Subject by id

@app.get('/subjects_by_id/{subject_id}')
async def subjects_by_id(id: int):
    subjects = await models.Subject.objects.get(id=id)
    return subjects


# Get Marks by id

@app.get('/marks_by_id/{marks_id}')
async def marks_by_id(id: int):
    marks = await models.Marks.objects.get(id=id)
    return marks


# Add student

@app.post('/add_student')
async def add_student(student: schema.StudentSchema):
    students = models.Student(name=student.name)
    response = await students.save()
    return response


# Add Subject

@app.post('/add_subject')
async def add_subject(subject: schema.SubjectSchema):
    subjects = models.Subject(name=subject.name)
    response = await subjects.save()
    return response


# Add Marks

@app.post('/add_marks')
async def add_mark(mark: schema.MarksSchema):
    marks = models.Marks(student_id=mark.student_id, subject_id=mark.subject_id, marks=mark.marks)
    response = await marks.save()
    return response


# Update Student

@app.put('/update_student_by_id/{student_id}')
async def update_student(student_id: int, student: schema.StudentUpdateSchema):
    students = await models.Student.objects.get(id=student_id)
    students.id = student.id
    students.name = student.name
    response = await students.update()
    return response


# Update Subject

@app.put('/update_subject_by_id/{subject_id}')
async def update_subject(subject_id: int, subject: schema.SubjectUpdateSchema):
    subjects = await models.Subject.objects.get(id=subject_id)
    subjects.id = subject.id
    subjects.name = subject.name
    response = await subjects.update()
    return response


# Update Marks

@app.put('/update_mark_by_id/{mark_id}')
async def update_mark(mark_id: int, mark: schema.MarksUpdateSchema):
    marks = await models.Marks.objects.get(id=mark_id)
    print(marks)
    marks.id = mark.id
    marks.student_id = mark.student_id
    marks.subject_id = mark.subject_id
    marks.marks = mark.marks
    response = await marks.update()
    return response


# Delete Student

@app.delete('/delete_student_by_id/{student_id}')
async def delete_student(student_id: int):
    students = await models.Student.objects.get(id=student_id)
    response = await students.delete()
    return response


# Delete Subject

@app.delete('/delete_subject_by_id/{subject_id}')
async def delete_subject(subject_id: int):
    subjects = await models.Subject.objects.get(id=subject_id)
    response = await subjects.delete()
    return response


# Delete Mark

@app.delete('/delete_mark_by_id/{mark_id}')
async def delete_mark(mark_id: int):
    marks = await models.Marks.objects.get(id=mark_id)
    response = await marks.delete()
    return response


# fetch mark

@app.get('/fetch/{student_id}')
async def fetch_mark(student: int):
    students = await models.Student.objects.get(id=student)
    marks = await models.Marks.objects.filter(student_id=student).all()

    details = []
    for i in marks:
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        sub = schema.FetchMarksSchema(
            subject_id=i.subject_id.id,
            subject_name=subject_name.name,
            marks=i.marks
        )
        details.append(sub)
    response = schema.FetchStudentSchema(
        student_id=students.id,
        student_name=students.name,
        details=details
    )
    return response

@app.get('/fetch_all_students_marks')
async def fetch_all_mark():
    students_db = await models.Student.objects.all()
    #sub1 = db.query(models.Subject).all()

    students_list = []

    for students in students_db:
        mark = await models.Marks.objects.filter(student_id =students.id).all()
        details = []
        for i in mark:
            subject_id = i.subject_id.id
            subject_name = await models.Subject.objects.filter(id =subject_id).get()
            s = schema.FetchMarksSchema(
                subject_id=i.subject_id.id,
                subject_name=subject_name.name,
                marks=i.marks
            )
            details.append(s)
        response = schema.FetchStudentSchema(
            student_id=students.id,
            student_name=students.name,
            details=details
        )
        students_list.append(response)

    return schema.FetchAllStudentsSchema(
        students=students_list
    )




# save FPDF() class into a
# variable pdf
@app.get("/fetch_detail_for_one_student_in_pdf")
async def fetch_all_subject_mark(student: int):
    pdf = FPDF()

# Add a page
    pdf.add_page()

    pdf.set_font("Arial", size = 15)



    stu_count = 1

    students = await models.Student.objects.get(id=student)
    marks = await models.Marks.objects.filter(student_id=student).all()

    pdf.cell(200, 10, txt=f"{stu_count}. Student Name : {students.name}",
             ln=1, align='C')

    subj = 1
    for i in marks:
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        pdf.cell(200, 10, txt=f" {subj}.Subject Name : {subject_name.name}", ln=1, align='L')
        pdf.cell(200, 10, txt=f"  Subject Mark : {i.marks}", ln=1, align='L')
        subj += 1
        pdf.cell(200, 10, txt="", ln=1, align='L')
        stu_count += 1

    pdf.output(f"{students.id}_{students.name}.pdf")
    return f'/home/vetrivel/PycharmProjects/crud_operations/{students.id}--{students.name}.pdf'





