from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateTimeField, IntegerField, DateField, TimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from webapp.models import User
from flask_login import current_user

# create the forms that are gonna be used to enter data and store the data into database

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])  # with Email() validator we check if the input email is a valid email address
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])   # the confirm_password has to be equal to password
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user=User.query.filter_by(username=username.data).first()  # get the user with the given username ( we get the first so that the result is not a list)
        if user:  # if the user with that username exists
            raise ValidationError('This username is taken! Please choose a different one.')  # raise a validation error that will appear in the html file

    def validate_email(self, email):
        user=User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is taken! Please choose a different one.')  # raise a validation error that will appear in the html file



class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')  # if the user wants his email and password to be remembered (it is a True or a False)
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username: # if the user changed his username we check for possible username error ( the username being already in the database)
            user=User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('This username is taken! Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email: # if the user changed his email address we check for possible email error( the email being already in database)
            user=User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('This email is taken! Please choose a different one.')

class CreateCourseForm(FlaskForm):
    id = StringField('Id', validators=[DataRequired()])
    name=StringField('Name',validators=[DataRequired()])
    submit=SubmitField('Create')

class CreateAssignmentForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    deadline=DateTimeField('Deadline',format='%d-%m-%Y %H:%M',validators=[DataRequired()])
    submit=SubmitField('Create')

class CreateStudyTimeForm(FlaskForm):
    date=DateField('Date',format='%d-%m-%Y',validators=[DataRequired()])
    start=TimeField('Start Hour', format='%H:%M',validators=[DataRequired()])
    end=TimeField('Finish Hour', format='%H:%M',validators=[DataRequired()])
    submit=SubmitField('Create')

class CreateResourceForm(FlaskForm):
    name=StringField('Name',validators=[DataRequired()])
    # assignment_id=IntegerField('Assignment ID')
    submit=SubmitField('Create')
