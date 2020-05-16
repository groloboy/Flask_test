# views.py

from flask import render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, DateField
from passlib.hash import sha256_crypt
from functools import wraps

from app import app
from data import Articles

Articles = Articles()


# Config MySQL
app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] ='root'
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#INIT MYSQL
mysql = MySQL(app)
app.secret_key='secrect123'

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/articles')
def articles():
	return render_template('articles.html',articles = Articles)

@app.route('/article/<string:id>')
def article(id):
    return render_template('article.html', id = id)

class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Password do not match')
		])
	confirm = PasswordField('Confirm Password')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		# Create Cursor
		cur = mysql.connection.cursor()
	
		# Execute Query
		cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username,password))

		# Commit to DB
		mysql.connection.commit()

		# Close connection
		cur.close()
		flash('You are now registered and can log in', 'success')
		return redirect(url_for('index'))
	
	return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
	
		# Get Form Fields
		username = request.form['username']
		password_candidate = request.form['password']

		# Create cursor
		cur = mysql.connection.cursor()

		# Get user by username	
		result = cur.execute("SELECT * FROM users WHERE username =%s",[username])

		if result > 0:
			# Get stored hash
			data = cur.fetchone()
			password = data['password']

			# Compare Passwords
			if sha256_crypt.verify(password_candidate, password):
				# Passed
				session['logged_in'] = True
				session['username'] = username
				flash('You are logged in', 'success')
				app.logger.info('PASSWORD MATCHED')
				return redirect(url_for('dashboard'))		
			else:
				app.logger.info('PASSWORD NO MATCHED')
				error = 'Invalid login'
				return render_template('login.html', error=error)
		
			# Close connection
			cur.close()
		else:
			app.logger.info('NO USER')
			error = 'Username not found'
			return render_template('login.html', error=error)
			

	return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Plese login', 'danger')
			return redirect(url_for('login'))
	return wrap

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM articles')
	data = cur.fetchall()
	cur.close()
	return render_template('dashboard.html',articles = data)

# Logout
@app.route('/logout')
def logout():
	session.clear()
	flash('You are now logged out','success')
	return redirect(url_for('login'))	
            

class AddArticle(Form):
	title = StringField('Title', [validators.Length(min=1, max=50)])
	body = StringField('Body')
	author = StringField('Author', [validators.Length(min=1, max=50)])

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	form = AddArticle(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		author = form.author.data
		# Create Cursor
		cur = mysql.connection.cursor()	
		# Execute Query
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, author))
		# Commit to DB
		mysql.connection.commit()
		# Close connection
		cur.close()
		flash('You are now registered and can log in', 'success')
		return redirect(url_for('dashboard'))	
	return render_template('add_article.html', form=form)

@app.route('/delete_article/<string:id>', methods = ['POST','GET'])
@is_logged_in
def delete_article(id):
    cur = mysql.connection.cursor()
    cur.execute('DELETE FROM articles WHERE id = {0}'.format(id))
    mysql.connection.commit()
    flash('Articles Removed Successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/edit_article/<id>', methods = ['POST', 'GET'])
@is_logged_in
def edit_article(id):
	form = AddArticle(request.form)
	cur = mysql.connection.cursor()
	cur.execute('SELECT * FROM articles WHERE id = %s', (id))
	data = cur.fetchall()
	cur.close()
	return render_template('edit_article.html', article = data[0], form = form)

@app.route('/update/<id>', methods=['POST'])
@is_logged_in
def update_article(id):
	form = AddArticle(request.form)
	if request.method == 'POST':
		title = form.title.data
		body = form.body.data
		author = form.author.data
		cur = mysql.connection.cursor()
		cur.execute("""
            UPDATE articles
            SET title = %s, 
			body = %s, 
			author = %s
            WHERE id = %s
        """, (title, body, author, id))
		flash('Contact Updated Successfully', 'success')
		mysql.connection.commit()
		return redirect(url_for('dashboard'))