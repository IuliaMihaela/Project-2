import pytest
from flaskr import create_app
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
import flask
from webapp import *
from webapp.models import *
from webapp.routes import *
from webapp.forms import *


@pytest.fixture
def client():
    sqlalchemy = SQLAlchemy()
    sqlalchemy.init_app(app)

    app.config['TESTING']=True
    app.testing=True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    db.init_app(app)
    with app.app_context():
        with app.test_client() as client:
            db.create_all()
            yield client



def test_home(client):
    response=client.get('/home', follow_redirects=True)
    assert response.status_code == 200
    assert b"Welcome!" in response.data

def test_valid_registration(client):

    response = client.post('/register',
                                data=dict(username='iulia',email='iulia@gmail.com',
                                          password='test',
                                          confirm='test'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b"Already have an account?" in response.data
    assert b'Email' in response.data


def test_valid_login_logout(client):
    response = client.post('/login',
                                data=dict(form="", email='iulia@gmail.com', password='testing'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data
    # assert b'Welcome back, iulia!' in response.data
    assert b"Log In" in response.data

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Register' in response.data

    response = client.post('/login',
                           data=dict(form=LoginForm(),email='iulia@gmail.com', password='testing'),
                           follow_redirects=True)

    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data



def test_account(client):
    response = client.post('/login',
                           data=dict(form=LoginForm(),username='iulia',email='iulia@gmail.com', password='testing'),
                           follow_redirects=True)
    assert response.status_code == 200

    response1= client.get('/account', follow_redirects=True)

    assert response1.status_code == 200
    # assert b"Username"  in  response.data
    # assert b'Email' in response.data
    # assert b'Account Info' in response1.data
    # assert b'iulia@gmail.com' in response1.data
    # assert b'iulia' in response1.data
    assert b'Welcome back, iulia!' in response.data

def test_new_course(client):
    response = client.post('/login',
                          data=dict( email='iulia@gmail.com', password='testing'),
                          follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/course/new', data=dict(form="",id='MA2',name='Mathematics 2'), follow_redirects=True)
    assert response.status_code == 200
    assert b"New Course" in response.data
    assert b"Courses" in response.data
    # assert b"Name" in response.data

def test_course(client):
    response = client.post('/login',
                           data=dict(email='iulia@gmail.com', password='testing'),
                           follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/course/<course_id>', data=dict(id='MA2', name='Mathematics 2'), follow_redirects=True)
    assert response.status_code == 200
    assert b"Update" in response.data



