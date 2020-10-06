from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, Email, ValidationError
from flaskblog.models import User
from flask_login import current_user



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

class UpdateAccountForm(FlaskForm):
	'''Creating registration form '''
	username = StringField('Username', validators = [DataRequired(), Length(min=4, max=25)])
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	picture = FileField('Upload your profile picture', validators=[FileAllowed(['jpg','png'])])
	submit = SubmitField("Update")

	def validate_username(self,username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError("Username already exist")

	def validate_email(self,email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError("Email already taken")


class RequestResetForm(FlaskForm):
	'''Creating Login form '''
	email = StringField('Email Address', validators = [DataRequired(), Email()])
	submit = SubmitField("Request Password Reset")

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError("There is no account with this email, You must register first.")

class PasswordResteForm(FlaskForm):
	'''Creating Login form '''
	password = PasswordField('Password', validators = [DataRequired(), Length(min=4)])
	confirm_password = PasswordField("Confirm Password", validators = [DataRequired(), EqualTo("password")])
	submit = SubmitField("Reset Password")
