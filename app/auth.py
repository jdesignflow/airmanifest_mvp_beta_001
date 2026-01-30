import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        dob = request.form['dob']
        
        db = get_db()
        cursor = None
        error = None

        # Safety Check: Ensure DB connected
        if db is None:
            error = "Database connection failed. Please check your internet or credentials."
        else:
            cursor = db.cursor(dictionary=True)

        if not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif not first_name:
            error = 'First Name is required.'
        elif not last_name:
            error = 'Last Name is required.'
        elif not dob:
            error = 'Date of Birth is required.'

        if error is None and cursor:
            try:
                # Check if user already exists
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone() is not None:
                    error = f"User {email} is already registered."
                else:
                    # Insert new user with DOB
                    cursor.execute(
                        "INSERT INTO users (email, password_hash, first_name, last_name, dob) VALUES (%s, %s, %s, %s, %s)",
                        (email, generate_password_hash(password), first_name, last_name, dob),
                    )
                    return redirect(url_for('auth.login'))
            except Exception as e:
                error = f"Registration failed: {str(e)}"

        flash(error)

    return render_template('auth/signup.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        
        if db is None:
            error = "Database connection failed."
        else:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user is None:
                error = 'Incorrect email.'
            elif not check_password_hash(user['password_hash'], password):
                error = 'Incorrect password.'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                session['role'] = user['role']
                if user['role'] == 'admin':
                    return redirect(url_for('admin.dashboard'))
                return redirect(url_for('traveler.dashboard'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.index'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        if db:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            g.user = cursor.fetchone()
        else:
            g.user = None

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view