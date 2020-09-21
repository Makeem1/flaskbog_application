from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from flaskblog.models import User



class RegistrationForm(FlaskForm):
	'''Creating registration form '''
	username = StringField('Username', validators = [DataRequired(), Length(min=4, max=25)])
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators = [DataRequired(), Length(min=4)])
	confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
	submit = SubmitField("Sign Up")

	def validate_username(self,username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError("Username already exist")

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError("Email already taken")


class LoginForm(FlaskForm):
	'''Creating Login form '''
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	password = PasswordField('Password', validators = [DataRequired()])
	remember = BooleanField("Remember Me")
	submit = SubmitField("Login")







