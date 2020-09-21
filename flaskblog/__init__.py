from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)

'''This code below is called secret name, which help to prevent the site from being 
attacked. This is called the csrf token key.
'''
app.config["SECRET_KEY"] = "99b6562bf2d1cf9ab461e439c5ebc27f"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'   #setting a database file on the same working directory called site.db

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from flaskblog import routes  