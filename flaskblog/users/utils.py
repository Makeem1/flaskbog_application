
import os
from PIL import Image
import secrets
from flask_mail import Message 
from flask_mail import Mail
from flaskblog import app, mail




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

 
# This is message that will be send if the user forget is/her user
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request', sender='noreply@demo.com',
											recipients=[user.email])
	msg.body = f''' Folllow the steps below to reset your passord in the link below:
{url_for("users.reset_token", token=token, _external = True )}.

If you did not make this request kindly ignore this message. No changes will be apply 
''' 
	mail.send(msg)
