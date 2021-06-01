from webapp import db, login_manager
from datetime import datetime
from flask_login import UserMixin

@login_manager.user_loader  # tells Flask-login how to load users given an id
def load_user(user_id):
    # Given an user_id, it returns the associated User object
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):  # UserMixin class provides the implementation of properties: is_authenticated(), is_active(), is_anonymous(), get_id()
    id=db.Column(db.Integer, primary_key=True)
    # the username and the password have to be unique
    username=db.Column(db.String(20),unique=True,nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(60),nullable=False)
    courses=db.relationship('Course',backref='user',lazy=True)
    # db.relationship return a new property, it point to Course, so it loads multiple courses in a list
    # backref is a way to declare a new property on the Course class; you can call course.user to get the user object
    # lazy defines when SQLAlchemy will load the data from the database
    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Course(db.Model):
    id = db.Column(db.String(60), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    assignments=db.relationship('Assignment',backref='course',lazy=True)
    study_times = db.relationship('StudyTime', backref='course', lazy=True)
    resources=db.relationship('Resource',backref='course',lazy=True)
    def __repr__(self):
        return f"Course('{self.id}','{self.name}')"


class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(255),nullable=False)
    deadline=db.Column(db.DateTime,nullable=False)
    completion_date=db.Column(db.DateTime)
    course_id=db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    resources = db.relationship('Resource', backref='assignment', lazy=True)
    def __repr__(self):
        return f"Assignment('{self.name}','{self.course_id}','{self.deadline}')"


class StudyTime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date=db.Column(db.Date,nullable=False)
    start_time=db.Column(db.Time,nullable=False)
    end_time=db.Column(db.Time,nullable=False)
    course_id=db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    def __repr__(self):
        return f"StudyTime('{self.date}','{self.spent_time}','{self.course_id}')"


class Resource(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String,nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'))
