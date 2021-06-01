import datetime

from flask import render_template, url_for, flash, redirect, request
from webapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, CreateCourseForm, CreateAssignmentForm, CreateStudyTimeForm, CreateResourceForm
from webapp import db, bcrypt, app
from webapp.models import *
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html', user=current_user)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit(): # the form doesn't have any input errors
        hashed_password=bcrypt.generate_password_hash(form.password.data).decode('utf-8')  # BCrypt internally generates a string while encoding passwords and stores that string along with the encrypted password
        user=User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)  # add user to database
        db.session.commit()  # ave changes to database
        flash('Your account has been created! You are now able to log in!', 'success')  # give feedback to the user by flashing a message
        return redirect(url_for('login'))   # redirect to an url for the login function
    return render_template('register.html', title='Register', form=form)  # render the register html template


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()  # make an instance for login form
    if form.validate_on_submit():  # if the form is valid when submitting( correct username and password)
        user=User.query.filter_by(email=form.email.data).first()  # get the user with the same email as the one submitted in the form
        if user and bcrypt.check_password_hash(user.password, form.password.data):  # if the user exits and the password entered in form is the same as the in the databases
            login_user(user,remember=form.remember.data)
            next_page=request.args.get('next') # is None if 'next' doesn't exist
            return redirect(next_page) if next_page else redirect(url_for(('home')))  # redirect tp home page if 'next page' doesn't exists
        else:
             flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)  # render the login template

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for(('home')))

@app.route("/account",methods=['GET','POST'])
@login_required  # if we are trying to access account without being logged in
def account():
    form=UpdateAccountForm()  # create an instance of the update account form
    if form.validate_on_submit():
        #change the username and the email of the current logged in user
        current_user.username=form.username.data
        current_user.email=form.email.data
        db.session.commit()  # save changes in database
        flash('Your account has been updated!','success')  # 'success' is a bootstrap class
        return redirect(url_for('account'))

    elif request.method=='GET': #if not submitting any changes
        # the user and the email are visible in the form
        form.username.data=current_user.username
        form.email.data=current_user.email
    return render_template('account.html', title='Account',form=form)

### course ###

@app.route("/course/new",methods=['GET','POST'])
@login_required
def new_course():
    form=CreateCourseForm()  # instance oof the new course form
    if form.validate_on_submit():
        course=Course(id=form.id.data+ '_'+str(current_user.id), name=form.name.data,user=current_user)  # create instance of the course with the data from the form
        db.session.add(course)  # add the course to the database
        db.session.commit()  # save changes to database
        flash('Your course has been created!','success')
        return redirect(url_for('all_courses'))  # redirect to the html page that contains the all courses
    return render_template('create_course.html', title='New Course',form=form, legend='New Course')


@app.route("/course/<course_id>")
@login_required
def course(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course.html',title=course.id, course=course)


@app.route("/course/<course_id>/update",methods=['GET','POST'])
@login_required
def update_course(course_id):
    course = Course.query.get_or_404(course_id)  # returns the course with the given id or a 404 error
    form=CreateCourseForm()
    if form.validate_on_submit():
        course.id=form.id.data
        course.name=form.name.data
        db.session.commit()
        flash('Your course has been updated!','success')
        return redirect (url_for('course',course_id=course.id))
    elif request.method=='GET':
        form.id.data=course.id
        form.name.data=course.name
    return render_template('create_course.html', title='Update Course',form=form, legend='Update Course')


@app.route("/course/<course_id>/delete",methods=['POST'])
@login_required
def delete_course(course_id):
    # course = Course.query.get_or_404((course_id,current_user.id))
    course = Course.query.get_or_404(course_id)
    db.session.delete(course)
    db.session.commit()
    flash('Your course has been deleted!', 'success')
    return redirect(url_for('all_courses', course_id=course.id))


@app.route("/courses")
@login_required
def all_courses():
    courses=Course.query.filter_by(user_id=current_user.id) # get all the courses for the current user
    return render_template('courses.html',courses=courses)

### assignment ###

@app.route("/course/<course_id>/assignment/new",methods=['GET','POST'])
@login_required
def new_assignment(course_id):
    form=CreateAssignmentForm()
    if form.validate_on_submit():
        course = Course.query.get_or_404(course_id) # get the course with the given id or a 404 error if the course isn't found
        assignment=Assignment(name=form.name.data,deadline=form.deadline.data,course=course)  # create instance of Assignment
        db.session.add(assignment)  # add assignment to databases
        db.session.commit()  # save changes
        flash('Your assignment has been created!','success')
        return redirect(url_for('course_assignments',course_id=course.id))
    return render_template('create_assignment.html', title='New Assignment',form=form, legend='New Assignment')


@app.route("/course/<course_id>/assignment/<assignment_id>")
@login_required
def assignment(course_id, assignment_id):
    # check if assignment and course with the given ids exist
    assignment=Assignment.query.get_or_404(assignment_id)
    course=Course.query.get_or_404(course_id)
    return render_template('assignment.html',title=assignment.id, assignment=assignment)

@app.route("/course/<course_id>/assignment/<assignment_id>/update",methods=['GET','POST'])
@login_required
def update_assignment(course_id,assignment_id):
    # check if assignment and course with the given ids exist
    course = Course.query.get_or_404(course_id)
    assignment=Assignment.query.get_or_404(assignment_id)
    form=CreateAssignmentForm()
    if form.validate_on_submit():
        # change current assignment data with the data submitted in the form
        assignment.deadline=form.deadline.data
        assignment.name=form.name.data
        db.session.commit()
        flash('Your assignment has been updated!','success')
        return redirect (url_for('assignment',course_id=course.id, assignment_id=assignment.id))
    elif request.method=='GET':
        # the form is filled with the assignment's current data
        form.deadline.data=assignment.deadline
        form.name.data=assignment.name
    return render_template('create_assignment.html', title='Update Assignment',form=form, legend='Update Assignment')


@app.route("/course/<course_id>/assignment/<assignment_id>/delete",methods=['POST'])
@login_required
def delete_assignment(course_id,assignment_id):
    course = Course.query.get_or_404(course_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    db.session.delete(assignment)  # delete from the database the assignment
    db.session.commit()
    flash('Your assignment has been deleted!', 'success')
    return redirect(url_for('course', course_id=course.id))

@app.route("/course/<course_id>/assignment/<assignment_id>/complete",methods=['GET','POST'])
@login_required
def complete_assignment(course_id,assignment_id):
    course = Course.query.get_or_404(course_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    assignment.completion_date=datetime.utcnow()  # add the current date and time
    db.session.commit()
    flash('Your assignment is completed!', 'success')
    return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))

@app.route("/course/<course_id>/assignment/<assignment_id>/incomplete",methods=['GET','POST'])
@login_required
def incomplete_assignment(course_id,assignment_id):
    course = Course.query.get_or_404(course_id)
    assignment = Assignment.query.get_or_404(assignment_id)
    assignment.completion_date=None  # set the completion date to Null in database
    db.session.commit()
    flash('Your assignment is incompleted!', 'success')
    return redirect(url_for('assignment', course_id=course.id, assignment_id=assignment.id))


@app.route("/course/<course_id>/assignments")
@login_required
def course_assignments(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_assignments.html', course=course)  # render the template that has all asignments for a specific course


@app.route("/assignments")
@login_required
def all_assignments():
    courses=Course.query.filter_by(user_id=current_user.id)  # get all the courses of the current user
    return render_template('all_assignments.html',courses=courses)  # render the template that has all assigments together

### study time ###

@app.route("/course/<course_id>/studytime/new",methods=['GET','POST'])
@login_required
def new_study_time(course_id):
    form=CreateStudyTimeForm()  # create instance of the form used for creating a study time
    if form.validate_on_submit():
        course = Course.query.get_or_404(course_id)
        study_time=StudyTime(date=form.date.data,start_time=form.start.data,end_time=form.end.data,course=course)  # create instance of study time with the data from the form
        db.session.add(study_time)  # add study time to the database
        db.session.commit()  # save changes
        flash('Your study time has been created!','success')
        return redirect(url_for('course_study_times',course_id=course.id))  # after creating a study time, the used is redirected to the page with all study times of the specific course
    return render_template('create_study_time.html', title='New Study Time',form=form, legend='New Study Time')


@app.route("/course/<course_id>/studytimes")
@login_required
def course_study_times(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_study_times.html', course=course)  # render the html template that has all study times for the specific course



@app.route("/course/<course_id>/studytime/<studytime_id>")
@login_required
def study_time(course_id, studytime_id):
    # check if both the course and the study time exist
    study_time=StudyTime.query.get_or_404(studytime_id)
    course=Course.query.get_or_404(course_id)
    return render_template('studytime.html',title=study_time.id, study_time=study_time)  # render the html template that has information about the study time


@app.route("/course/<course_id>/studytime/<studytime_id>/update",methods=['GET','POST'])
@login_required
def update_study_time(course_id,studytime_id):
    course = Course.query.get_or_404(course_id)
    study_time=StudyTime.query.get_or_404(studytime_id)
    form=CreateStudyTimeForm()
    if form.validate_on_submit():
        # the study time data si updated to the new one from the form
        study_time.date=form.date.data
        study_time.start_time=form.start.data
        study_time.end_time = form.end.data
        db.session.commit()
        flash('Your study time has been updated!','success')
        return redirect (url_for('course_study_times',course_id=course.id))
    elif request.method=='GET':
        # the form is filled with the study time current data
        form.date.data=study_time.date
        form.start.data=study_time.start_time
        form.end.data = study_time.end_time
    return render_template('create_study_time.html', title='Update Study Time',form=form, legend='Update Study Time')


@app.route("/course/<course_id>/studytime/<studytime_id>/delete",methods=['POST'])
@login_required
def delete_study_time(course_id,studytime_id):
    course = Course.query.get_or_404(course_id)
    study_time = StudyTime.query.get_or_404(studytime_id)
    db.session.delete(study_time)  # delete study time from database
    db.session.commit()
    flash('Your assignment has been deleted!', 'success')
    return redirect(url_for('course_study_times', course_id=course.id))  # return to all current study times of the given course

### resource ###

@app.route("/course/<course_id>/resource/new",methods=['GET','POST'])
@login_required
def new_resource(course_id):
    form=CreateResourceForm()  # instance of the form
    if form.validate_on_submit():
        course = Course.query.get_or_404(course_id)
        resource=Resource(name=form.name.data,course=course)  # instance of the new resource
        db.session.add(resource)
        db.session.commit()
        flash('Your resource has been created!','success')
        return redirect(url_for('course_resources',course_id=course.id))  # redirect to all the course's resources
    return render_template('create_resource.html', title='New Resource',form=form, legend='New Resource')


@app.route("/course/<course_id>/resources")
@login_required
def course_resources(course_id):
    course = Course.query.get_or_404(course_id)
    return render_template('course_resources.html', course=course)  # render the html template with all resources for the specific course

#############
@app.route("/course/<course_id>/resource/<resource_id>")
@login_required
def resource(course_id, resource_id):
    # check if both resource and course exist
    resource=Resource.query.get_or_404(resource_id)
    course=Course.query.get_or_404(course_id)
    return render_template('resource.html',title=resource.id, resource=resource)  # render the html templete with the details about the given resource


@app.route("/course/<course_id>/resource/<resource_id>/update",methods=['GET','POST'])
@login_required
def update_resource(course_id,resource_id):
    course = Course.query.get_or_404(course_id)
    resource=Resource.query.get_or_404(resource_id)
    form=CreateResourceForm()  # instance of the resource form
    if form.validate_on_submit():
        #change current resource name to the name entered in form
        resource.name=form.name.data
        db.session.commit()
        flash('Your resource has been updated!','success')
        return redirect (url_for('course_resources',course_id=course.id))
    elif request.method=='GET':
        # fill in the form input with the current name of the resource
        form.name.data=resource.name
    return render_template('create_resource.html', title='Update Resource',form=form, legend='Update Resource')


@app.route("/course/<course_id>/resource/<resource_id>/delete",methods=['POST'])
@login_required
def delete_resource(course_id,resource_id):
    course = Course.query.get_or_404(course_id)
    resource = StudyTime.query.get_or_404(resource_id)
    db.session.delete(resource)  # delete resource from database
    db.session.commit()
    flash('Your resource has been deleted!', 'success')
    return redirect(url_for('course_resources', course_id=course.id))  # redirect to all resource of the course
