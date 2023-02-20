import functools

# This project uses 2 Blueprints one for blog and other authentication
# Blueprint is way to organize related views and other code
from flask import(Blueprint, flash, g, redirect, render_template, request, session,
                  url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

# the second parameter name shows where the blueprint object is defines
# url_prefix will be prefixed to all URLs linked to Blueprint
bp = Blueprint('auth',__name__,url_prefix='/auth')

# auth blueprint has 2 views 
# 1) to register new users
# 2) to login 
# 3) to logout

# The First View: Register
# /auth/register URL
# register view will return HTML

@bp.route('/register', methods=('GET','POST'))
def register():
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None

        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username,password) VALUES (?,?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods = ('GET','POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'],password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id']= user['id']
            return redirect(url_for('index'))
        
        flash(error)

    return render_template('auth/login.html')

# check if session id is stored in the session and 
# get that user's data from DB executing query
@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    # store data on g.user for the length of the request
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?',(user_id,)
        ).fetchone()


@bp.route('logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# a decorator that checks logged in status for users in 
# all views
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # if user not logged in always send him to login
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# base.html
# <!--Templates are files that contain static data as well as placeholders for dynamic data.
# flask uses jinja template library to render templates-->

# <!--In jinja anything between {{ and }} is an expression which is final output {% and %} denotes
# control flow like if and for. It has start and end tag-->
