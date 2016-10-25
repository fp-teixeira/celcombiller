from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.restless
from flask.ext.login import LoginManager
from flask.ext.cors import CORS
from config import PATH_TO_DATABASE, SECRET_KEY, DEBUG

# Create the Flask application and the Flask-SQLAlchemy object.
app = flask.Flask(__name__)
app.config['DEBUG'] = DEBUG
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../' + PATH_TO_DATABASE


# Ability cross domain
cors = CORS(app)

db = SQLAlchemy(app)

app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
