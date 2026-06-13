from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class Department(db.Model):
    __tablename__ = 'department'
    dept_id = db.Column(db.String(10), primary_key=True)
    dept_name = db.Column(db.String(50))
    dean = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    office = db.Column(db.String(50))
    majors = db.relationship('Major', backref='department', lazy=True)

class Major(db.Model):
    __tablename__ = 'major'
    major_id = db.Column(db.String(10), primary_key=True)
    major_name = db.Column(db.String(50))
    dept_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'))
    duration = db.Column(db.SmallInteger)
    degree_type = db.Column(db.String(20))
    classes = db.relationship('Class', backref='major', lazy=True)

class Class(db.Model):
    __tablename__ = 'classes'
    class_id = db.Column(db.String(10), primary_key=True)
    class_name = db.Column(db.String(50))
    major_id = db.Column(db.String(10), db.ForeignKey('major.major_id'))
    counselor_id = db.Column(db.String(20)) 
    grade = db.Column(db.Integer)
    students = db.relationship('Student', backref='class_', lazy=True)

class Student(db.Model):
    __tablename__ = 'student'
    stu_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(30))
    gender = db.Column(db.String(2))
    birth = db.Column(db.Date)
    ethnicity = db.Column(db.String(20))
    political_status = db.Column(db.String(20))
    native_place = db.Column(db.String(50))
    id_card = db.Column(db.String(18))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(50))
    address = db.Column(db.String(100))
    enrollment_year = db.Column(db.Integer)
    status = db.Column(db.String(10), default='在读')
    photo_path = db.Column(db.String(200))
    resume_path = db.Column(db.String(200))
    class_id = db.Column(db.String(10), db.ForeignKey('classes.class_id'))
    major_changes = db.relationship('MajorChange', backref='student', lazy=True)
    awards = db.relationship('Award', backref='student', lazy=True)
    punishments = db.relationship('Punishment', backref='student', lazy=True)
    enrollments = db.relationship('Enrollment', backref='student', lazy=True)
    summary = db.relationship('StudentSummary', uselist=False, backref='student')

class MajorChange(db.Model):
    __tablename__ = 'major_change'
    change_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_id = db.Column(db.String(20), db.ForeignKey('student.stu_id'))
    origin_major = db.Column(db.String(10))
    new_major = db.Column(db.String(10))
    change_date = db.Column(db.Date)
    approval_doc = db.Column(db.String(50))
    reason = db.Column(db.String(200))
    operator = db.Column(db.String(20))

class Award(db.Model):
    __tablename__ = 'award'
    award_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_id = db.Column(db.String(20), db.ForeignKey('student.stu_id'))
    award_name = db.Column(db.String(50))
    award_level = db.Column(db.String(20))
    award_date = db.Column(db.Date)
    issuer = db.Column(db.String(50))
    certificate_path = db.Column(db.String(200))

class Punishment(db.Model):
    __tablename__ = 'punishment'
    punish_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_id = db.Column(db.String(20), db.ForeignKey('student.stu_id'))
    punish_type = db.Column(db.String(20))
    punish_date = db.Column(db.Date)
    reason = db.Column(db.String(200))
    lift_date = db.Column(db.Date)
    file_path = db.Column(db.String(200))

class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.String(10), primary_key=True)
    course_name = db.Column(db.String(50))
    credit = db.Column(db.Float(asdecimal=True))
    hours = db.Column(db.SmallInteger)
    dept_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'))
    course_type = db.Column(db.String(10))
    syllabus_path = db.Column(db.String(200))
    teacher_id = db.Column(db.String(20))
    dept = db.relationship('Department', backref='courses')

class Enrollment(db.Model):
    __tablename__ = 'enrollment'
    enroll_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    stu_id = db.Column(db.String(20), db.ForeignKey('student.stu_id'))
    course_id = db.Column(db.String(10), db.ForeignKey('course.course_id'))
    semester = db.Column(db.String(20))
    enroll_date = db.Column(db.Date)
    course = db.relationship('Course', backref='enrollments')
    score = db.relationship('Score', uselist=False, backref='enrollment')

class Score(db.Model):
    __tablename__ = 'score'
    score_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    enroll_id = db.Column(db.Integer, db.ForeignKey('enrollment.enroll_id'), unique=True)
    regular_score = db.Column(db.Float(asdecimal=True))
    final_score = db.Column(db.Float(asdecimal=True))
    total_score = db.Column(db.Float(asdecimal=True))
    exam_method = db.Column(db.String(10))
    makeup_score = db.Column(db.Float(asdecimal=True))

class StudentSummary(db.Model):
    __tablename__ = 'student_summary'
    stu_id = db.Column(db.String(20), db.ForeignKey('student.stu_id'), primary_key=True)
    total_credits = db.Column(db.Float(asdecimal=True), default=0)
    gpa = db.Column(db.Float(asdecimal=True), default=0)
    has_punish = db.Column(db.Boolean, default=False)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(30))
    dept_id = db.Column(db.String(10), db.ForeignKey('department.dept_id'))
    related_id = db.Column(db.String(20))
    last_login = db.Column(db.DateTime)
    dept = db.relationship('Department', backref='teachers', lazy=True)

    def get_id(self):
        return str(self.user_id)