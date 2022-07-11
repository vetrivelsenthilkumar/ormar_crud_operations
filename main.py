import schema
import models
from database import database
from fastapi import FastAPI, BackgroundTasks
from fpdf import FPDF, HTMLMixin
from generatepdf import student_details
from generate_excel import Writer
from time import sleep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

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
    # sub1 = db.query(models.Subject).all()

    students_list = []

    for students in students_db:
        mark = await models.Marks.objects.filter(student_id=students.id).all()
        details = []
        for i in mark:
            subject_id = i.subject_id.id
            subject_name = await models.Subject.objects.filter(id=subject_id).get()
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
    pdf = student_details()
    pdf.create_pdf()

    pdf.set_font("Arial", 15)

    stu_count = 1

    students = await models.Student.objects.get(id=student)
    marks = await models.Marks.objects.filter(student_id=student).all()

    pdf.write_pdf(f'{stu_count}. Student Name : {students.name}',
                  'C')

    subj = 1
    for i in marks:
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        pdf.write_pdf(f" {subj}.Subject Name : {subject_name.name}", 'L')
        pdf.write_pdf(f"  Subject Mark : {i.marks}", 'L')
        subj += 1
        pdf.write_pdf("", 'L')
        stu_count += 1

    pdf.generate_pdf(f"{students.id}_{students.name}")
    return f'/home/vetrivel/PycharmProjects/crud_operations/{students.id}--{students.name}.pdf'


@app.get("/create_student_report_card")
async def fetch_all_subject_mark(student_id: int):
    students = await models.Student.objects.get(id=student_id)
    marks = await models.Marks.objects.filter(student_id=student_id).all()
    result = []
    s = 1

    class StudentPdf(FPDF, HTMLMixin):
        pass

    student_html = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <h1 align="center">Report Card</h1>
                        <h2 align="left"> Name of the Student: {students.name}    Student Id:{students.id}</h2>
                    </head>
                    
                    <body>
                        <table style="width:90% border: 1px solid black;" class = "class" width="100%" border="1" height="100%" align="center">
                        <thead>
                        <tr>
                        <th width="20%" > S.No</th>
                        <th width="20%" > Subject</th>
                        <th width="20%" > Mark</th>
                        <th width="20%" > Result</th>
                        </tr>
                        </thead>
                        <tbody class="text-center text-sm">
                                                """
    s_no = 0
    total = 0
    for i in marks:
        total += i.marks
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        s_no += 1
        if i.marks >= 50:
            Result = "PASS"
            result.append(Result)
        else:
            Result = "FAIL"
            result.append(Result)

        student_html += "<tr>"
        student_html += """<td align="center" font face="Arial">""" + str(s_no) + "</td>"
        student_html += """<td align="center" >""" + subject_name.name + "</td>"
        student_html += """<td align="center" >""" + str(i.marks) + "</td>"
        if Result == "PASS":
            student_html += """<td align="center"> """ + Result + "</td>"
        else:
            student_html += """<td  align="center"><font color="#FF0000">""" + Result + "</font></td>"
        student_html += "</tr>"

        # student_html += """</tbody></table></body></html>"""
        s += 1
    for i in result:
        if i == "FAIL":
            result = "FAIL"
            break
        else:
            result = "PASS"
    if result == "PASS":
        student_html += f"""
                            </tbody>
                            <tbody width="200%">
                            <tr text-align="center">
                                <th colspan="2"  align="left">Result: {result}</th>
                                <th colspan="2" align="left">Total: {total}</th>
                            </tr>
                              """
    else:
        student_html += f"""
                                </tbody>
                                <tbody width="200%">
                                <tr text-align="center">
                                    <th colspan="2"  align="left"><font color="#FF0000">Result: {result}</font></th>
                                    <th colspan="2" align="left">Total: {total}</th>
                                </tr>
                                """
        student_html += """</tbody></table></body></html>"""
    pdf = StudentPdf()
    pdf.add_page()
    pdf.write_html(student_html)
    pdf.output(f"{students.name}.pdf")


# f"{students.name}.pdf"


@app.get("/fetch_student_record_csv_file")
async def fetch_data_in_csv_file(student_id: int):
    result = None
    students = await models.Student.objects.get(id=student_id)
    marks = await models.Marks.objects.filter(student_id=student_id).all()
    writer = Writer()
    writer.create_writer(f"{students.name}.xlsx")
    row = 0
    col = 0
    writer.write_excel(row, col, "S.No")
    writer.write_excel(row, col + 1, "Subject_Name")
    writer.write_excel(row, col + 2, "Marks")
    writer.write_excel(row, col + 3, "Result")
    s_no = 1
    # s_no +=1
    total = 0
    subj = 1
    result = []
    for i in marks:
        total += i.marks
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        if i.marks >= 50:
            Result = "PASS"
            result.append(Result)
        else:
            Result = "FAIL"
            result.append(Result)

        writer.write_excel(row + 1, col, s_no)
        writer.write_excel(row + 1, col + 1, subject_name.name)
        writer.write_excel(row + 1, col + 2, i.marks)
        writer.write_excel(row + 1, col + 3, Result)
        row += 1
        s_no += 1
    for i in result:
        if i == "FAIL":
            result = "FAIL"
            break
        else:
            result = "PASS"
    writer.write_excel(row + 1, col, f"Result:{result}")
    writer.write_excel(row + 1, col + 2, f"Total:{total}")
    writer.close_excel()


'''def send_email_pdf(message):
    sleep(5)
    print('Sending email:', message)'''

@app.get('/send_email_pdf_file')
async def mail(student_id: int):
    #attach1 = fetch_all_subject_mark(student_id)
    #background_tasks.add_task(fetch_all_subject_mark, 1)
    #background_tasks.add_task(fetch_data_in_csv_file, 2)
    #background_tasks.add_task(send_email, "Hi Welcome")
    sleep(5)
    students = await models.Student.objects.get(id=student_id)
    marks = await models.Marks.objects.filter(student_id=student_id).all()
    result = []
    s = 1

    class StudentPdf(FPDF, HTMLMixin):
        pass

    student_html = f"""
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <h1 align="center">Report Card</h1>
                            <h2 align="left"> Name of the Student: {students.name}    Student Id:{students.id}</h2>
                        </head>

                        <body>
                            <table style="width:90% border: 1px solid black;" class = "class" width="100%" border="1" height="100%" align="center">
                            <thead>
                            <tr>
                            <th width="20%" > S.No</th>
                            <th width="20%" > Subject</th>
                            <th width="20%" > Mark</th>
                            <th width="20%" > Result</th>
                            </tr>
                            </thead>
                            <tbody class="text-center text-sm">
                                                    """
    s_no = 0
    total = 0
    for i in marks:
        total += i.marks
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        s_no += 1
        if i.marks >= 50:
            Result = "PASS"
            result.append(Result)
        else:
            Result = "FAIL"
            result.append(Result)

        student_html += "<tr>"
        student_html += """<td align="center" font face="Arial">""" + str(s_no) + "</td>"
        student_html += """<td align="center" >""" + subject_name.name + "</td>"
        student_html += """<td align="center" >""" + str(i.marks) + "</td>"
        if Result == "PASS":
            student_html += """<td align="center"> """ + Result + "</td>"
        else:
            student_html += """<td  align="center"><font color="#FF0000">""" + Result + "</font></td>"
        student_html += "</tr>"

        # student_html += """</tbody></table></body></html>"""
        s += 1
    for i in result:
        if i == "FAIL":
            result = "FAIL"
            break
        else:
            result = "PASS"
    if result == "PASS":
        student_html += f"""
                                </tbody>
                                <tbody width="200%">
                                <tr text-align="center">
                                    <th colspan="2"  align="left">Result: {result}</th>
                                    <th colspan="2" align="left">Total: {total}</th>
                                </tr>
                                  """
    else:
        student_html += f"""
                                    </tbody>
                                    <tbody width="200%">
                                    <tr text-align="center">
                                        <th colspan="2"  align="left"><font color="#FF0000">Result: {result}</font></th>
                                        <th colspan="2" align="left">Total: {total}</th>
                                    </tr>
                                    """
        student_html += """</tbody></table></body></html>"""
    pdf = StudentPdf()
    pdf.add_page()
    pdf.write_html(student_html)
    pdf.output(f"{students.name}.pdf")
    mail_content = '''Student Details'''
    sender_address = 'vetrisenthilmkce@gmail.com'
    sender_pass = 'qxqmgpvvghmopyra'
    receiver_address = 'vetrisenthilmkce@gmail.com'
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file_name = f"{students.name}.pdf"
    attach_file = open(attach_file_name, 'rb')
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')
    return {'result': "Sent"}

'''def send_email_xlsx(message):
    sleep(5)
    print('Sending email:', message)'''

@app.get('/send_email_csv_file')
async def mail(student_id: int):
    sleep(5)
    result = None
    students = await models.Student.objects.get(id=student_id)
    marks = await models.Marks.objects.filter(student_id=student_id).all()
    writer = Writer()
    writer.create_writer(f"{students.name}.xlsx")
    row = 0
    col = 0
    writer.write_excel(row, col, "S.No")
    writer.write_excel(row, col + 1, "Subject_Name")
    writer.write_excel(row, col + 2, "Marks")
    writer.write_excel(row, col + 3, "Result")
    s_no = 1
    # s_no +=1
    total = 0
    subj = 1
    result = []
    for i in marks:
        total += i.marks
        subject_id = i.subject_id.id
        subject_name = await models.Subject.objects.filter(id=subject_id).get()
        if i.marks >= 50:
            Result = "PASS"
            result.append(Result)
        else:
            Result = "FAIL"
            result.append(Result)

        writer.write_excel(row + 1, col, s_no)
        writer.write_excel(row + 1, col + 1, subject_name.name)
        writer.write_excel(row + 1, col + 2, i.marks)
        writer.write_excel(row + 1, col + 3, Result)
        row += 1
        s_no += 1
    for i in result:
        if i == "FAIL":
            result = "FAIL"
            break
        else:
            result = "PASS"
    writer.write_excel(row + 1, col, f"Result:{result}")
    writer.write_excel(row + 1, col + 2, f"Total:{total}")
    writer.close_excel()
    mail_content = '''Student Details'''
    sender_address = 'vetrisenthilmkce@gmail.com'
    sender_pass = 'qxqmgpvvghmopyra'
    receiver_address = 'vetrisenthilmkce@gmail.com'
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = 'A test mail sent by Python. It has an attachment.'
    message.attach(MIMEText(mail_content, 'plain'))
    attach_file_name = f"{students.name}.xlsx"
    attach_file = open(attach_file_name, 'rb')
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload)
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print('Mail Sent')
    return {'result': "Sent"}




