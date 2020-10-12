from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config




'''This code below is called secret name, which help to prevent the site from being 
attacked. This is called the csrf token key.
'''
  #setting a database file on the same working directory called site.db

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'  # this view here is our login route
login_manager.login_message_category = 'info' # this category is a boostrap class

mail = Mail()


def create_app(config_class = Config):
	app = Flask(__name__)
	app.config.from_object(Config)

	db.init_app(app)
	login_manager.init_app(app)
	bcrypt.init_app(app)
	mail.init_app(app)

	from flaskblog.users.route import users  
	from flaskblog.posts.route import posts  
	from flaskblog.main.route import main 
	from flaskblog.error.handler import errors 
	app.register_blueprint(users)
	app.register_blueprint(posts)
	app.register_blueprint(main)
	app.register_blueprint(errors)

	return app


