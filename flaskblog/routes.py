import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request,abort
from flaskblog import app, db, bcrypt, mail
from flaskblog.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
														PostForm, RequestResetForm, PasswordResteForm)
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
import os
from flask_mail import Message 


# when double decorators is used on a function, both decorators are still
#pointing to the same function. Either "/" or "/home " still mean the same thing

@app.route('/home/')
@app.route('/')
def home():
	page = request.args.get('page',1, type = int)
	all_post = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', all_post = all_post )

@app.route('/about')
def about():
    return render_template('about.html', title="About Blog")

@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home')) 
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data)
		user = User(username=form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f"Your account has been created! You are now able to login", "success")
		return redirect(url_for("home"))
	return render_template('register.html', title="Register", form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit(): 
		user = User.query.filter_by(email = form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember = form.remember.data)
			next_page = request.args.get('next')   # Using request.atgs.get("next") to query if there's next page, will direct us to the page if it exist na d none if it does not
			if next_page:
				return redirect(next_page)
			else:
				return redirect(url_for('home'))
		else:
			flash("Log in unsuccessful. Please check username and password", "danger")
	return render_template('login.html', title="Login", form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_ , f_ext = os.path.splitext(form_picture.filename) # note the file upload will always have a filename extension
	picture_fn = random_hex + f_ext
	profile_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

	i = Image.open(form_picture)
	image_output = (125,125)
	i.thumbnail(image_output)
	i.save(profile_path)
	return picture_fn

@app.route('/account', methods=['GET', 'POST'])
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
		return redirect(url_for('account'))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email 
	user_image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
	return render_template('account.html', title ="Account", 
								user_image_file= user_image_file, form=form)


@app.route('/new/post', methods=['GET', 'POST'])
@login_required # This will require the anyone who want to access this page to login in first inorder to access it
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content = form.content.data, author=current_user)
		db.session.add(post) 
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title ="New Post", 
								form=form,  legend="New Post")


@app.route('/post/<int:post_id>')
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', title =post.title, post=post)


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required 
def update_post(post_id): 
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(404)
	form = PostForm()   
	if form.validate_on_submit():
		post.title = form.title.data
		post.content = form.content.data
		db.session.commit()
		flash("Your post has been updates!", 'success')
		return redirect(url_for('home'))
	elif request.method == "GET":
		form.title.data = post.title
		form.content.data = post.content
	return render_template('create_post.html', title ="Update Post", 
							form=form, legend="Update Post")


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required 
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if post.author != current_user:
		abort(404)
	db.session.delete(post)
	db.session.commit()
	flash('Your post has been deleted!', 'success')
	return redirect(url_for('home'))


@app.route('/user/<string:username>')
def user_posts(username):
	page = request.args.get('page', 1, type=int)
	user = User.query.filter_by(username=username).first_or_404()
	all_post = Post.query.filter_by(author=user)\
			.order_by(Post.date_posted.desc())\
			.paginate(page=page, per_page=5)
	return render_template('user_posts.html', all_post = all_post, user=user)

 
# This is message that will be send if the user forget is/her user
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com',
											recipients=[user.email])
	msg.body = f''' Folllow the steps below to reset your passord in the link below:
{url_for("reset_token", token=token, _external = True )}.

If you did not make this request kindly ignore this message. No changes will be apply 
''' 
	mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with instruction to reset your password', 'info')
	return render_template('reset_request.html', title ="Reset Password", 
								         form=form,  legend="Password Reset")


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash("That is an invalid or expired toke.", 'warning')
		return redirect(url_for('reset_request'))
	form = PasswordResteForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data)
		user.password = hashed_password
		db.session.commit()
		flash("Your password has been updated! You are now able to login", "success")
		return redirect(url_for("login"))
	return render_template('reset_token.html', title ="Reset Password", 
								         form=form,  legend="Password Reset")


