from flask import render_template, url_for, flash, redirect, request,abort, Blueprint
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
													RequestResetForm, PasswordResteForm)
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.users.utils import save_picture, send_reset_email
from flaskblog.models import User, Post

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.home')) 
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data)
		user = User(username=form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f"Your account has been created! You are now able to login", "success")
		return redirect(url_for("users.login"))
	return render_template('register.html', title="Register", form=form)

@users.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = LoginForm()
	if form.validate_on_submit(): 
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')   # Using request.atgs.get("next") to query if there's next page, will direct us to the page if it exist na d none if it does not
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('main.home'))
		else:
			flash("Log in unsuccessful. Please check username and password", "danger")
	return render_template('login.html', title="Login", form=form)


@users.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.home'))

@users.route('/account', methods=['GET', 'POST'])
@login_required  #This will require the anyone who want to access this page to login in first inorder to access it
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			profile_file = save_picture(form.picture.data)
			current_user.image_file =profile_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated', 'success')
		return redirect(url_for('users.account'))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email 
	user_image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
	return render_template('account.html', title ="Account", 
								user_image_file= user_image_file, form=form)


@users.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	all_post = Post.query.filter_by(author=user)\
			.order_by(Post.date_posted.desc())\
			.paginate(page=page, per_page=5)
	return render_template('user_posts.html', all_post = all_post, user=user)

@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instruction to reset your password', 'info')
	return render_template('reset_request.html', title ="Reset Password", 
								         form=form,  legend="Password Reset")


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash("That is an invalid or expired toke.", 'warning')
		return redirect(url_for('users.reset_request'))
	form = PasswordResteForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data)
		user.password = hashed_password
		db.session.commit()
		flash("Your password has been updated! You are now able to login", "success")
		return redirect(url_for("users.login"))
	return render_template('reset_token.html', title ="Reset Password", 
								         form=form,  legend="Password Reset")
