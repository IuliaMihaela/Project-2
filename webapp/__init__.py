from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from webapp.config import Config


app = Flask(__name__)  # create Flask application
app.config['SECRET_KEY']='7ef4aa839f699e98af3648ae74d32187'  # the number is from: import secrets; secrets.token_hex(16)
# load the configuration and then create the SQLAlchemy object by passing it the application.
# db provides a class called Model that is a declarative base which can be used to declare models
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
db=SQLAlchemy(app)

# bcrypt is a hashing function for password,
# it incorporates salt(additional input of random data that helps safeguard passwords when stored)
# for protecting the application against any attacks
bcrypt=Bcrypt(app)  # instantiate bcrypt object

#LoginManager provides user session management,
# it handles the common tasks of logging in, logging out, and remembering your users’ sessions over extended periods of time
login_manager=LoginManager(app)   # instantiate LoginManager object
# when a user attempts to access a login_required view without being logged in, Flask-Login will flash a message and redirect them to the log in view
# here we set it up to 'login'
login_manager.login_view='login'
login_manager.login_message_category='info'  # customize login message category (for bootstrap)

from webapp import routes


