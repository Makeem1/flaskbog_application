from flaskblog import create_app


app = create_app()

# the below code help solve the problem of solving environment variable at the command line
# with this code, there is no need of setting envinronment variable
if __name__ == '__main__':
	app.run(debug=True) 
 