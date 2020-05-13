# views.py

from flask import render_template

from app import app
from data import Articles

Articles = Articles()

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