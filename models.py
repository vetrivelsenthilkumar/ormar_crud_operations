import ormar
import sqlalchemy

from database import metadata, database, DATABASE_URL


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class Student(ormar.Model):
    class Meta(BaseMeta):
        tablename: str = 'Student'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=255)


class Subject(ormar.Model):
    class Meta(BaseMeta):
        tablename: str = 'Subject'

    id: int = ormar.Integer(primary_key=True)
    name: str = ormar.String(max_length=255)


class Marks(ormar.Model):
    class Meta(BaseMeta):
        tablename: str = 'Marks'

    id: int = ormar.Integer(primary_key=True)
    student_id: int = ormar.ForeignKey(Student, default=None)
    subject_id: int = ormar.ForeignKey(Subject, default=None)
    marks: int = ormar.Integer()


engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)
