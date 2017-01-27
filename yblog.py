# IDM CS7025, Simple Blog built with Flask
# login credentials - username: admin, password: admin

from flask import Flask, request, session, g, redirect, url_for, render_template, flash
from functools import wraps 
import sqlite3

app = Flask(__name__) 
app.config['SECRET_KEY'] = 'rw3^jyu_d*$8oi!m(4EiDp2^df' 
app.config['DATABASE'] = 'yblog.db'
app.config['USERNAME'] = 'admin'
app.config['PASSWORD'] = 'admin'

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login to view and post blogs.')
            return redirect(url_for('welcome'))
    return wrap

# login page is visible to visitors and members
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD'] :
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You are logged in.')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You are logged out.')
    return redirect(url_for('welcome'))

# welcome page, visible before and after login
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# hompepage, visible after login
@app.route('/')
@login_required
def index(methods=['GET', 'POST']):
    g.db = connect_db()
    g.db.execute("CREATE TABLE IF NOT EXISTS posts(title TEXT, description TEXT)")
    cur = g.db.execute('SELECT * FROM posts')
    posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
    g.db.close()
    return render_template('index.html', posts=posts)

#transition from (index.html) to (blog.html)
@app.route('/loading', methods=['POST'])
@login_required
def loading():
    session['title'] = request.form['title']
    session['description'] = request.form['description']
    return redirect(url_for('blog'))

@app.route('/blog')
@login_required
def blog(): 
    if 'title' and 'description' in session:
        a = session['title']
        b = session['description']
        # remove two sessions to ensure the entries are registered only once
        session.pop('title', None)
        session.pop('description', None)  
        # add the new entries to database
        g.db = connect_db()
        cur = g.db.cursor()
        cur.execute("INSERT INTO posts VALUES('"+a+"','"+b+"')")
        g.db.commit()
        # retrieve all entries
        cur.execute("SELECT * FROM posts")
        posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
        g.db.close()
        # return the needed variables for html rendering
        return render_template('blog.html', title=a, description=b, posts=posts)
    else:
        # when no new entries are received, display all the old entries
        g.db = connect_db()
        cur = g.db.execute('SELECT * FROM posts')
        posts = [dict(title=row[0], description=row[1]) for row in cur.fetchall()]
        g.db.close()
        return render_template('blog.html', posts=posts)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

if __name__ == '__main__':
    app.run(debug=True)
