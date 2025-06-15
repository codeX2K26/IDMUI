from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import ActivityLog, User
from app.utils.keystone_auth import keystone_authenticate
from app import db, csrf
from functools import wraps
from werkzeug.security import generate_password_hash

auth_bp = Blueprint('auth', __name__)

# Admin access decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Keystone user wrapper for Flask-Login
class KeystoneUser:
    def __init__(self, token, project_id, username):
        self.token = token
        self.project_id = project_id
        self.username = username
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return f"{self.username}|{self.token}|{self.project_id}"

# ✅ Login route with CSRF disabled
@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if request.method == 'POST' and 'login' in request.form:
        username = request.form['username']
        password = request.form['password']

        token, project_id = keystone_authenticate(username, password)

        if token:
            user = KeystoneUser(token, project_id, username)
            login_user(user)

            # Log activity
            activity = ActivityLog(
                user_id=username,
                action='User logged in via Keystone',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            flash('Login successful', 'success')
            return redirect(url_for('service_management.dashboard'))
        else:
            flash('Invalid credentials or Keystone authentication failed.', 'danger')

    return render_template('auth/login.html')

# ✅ Registration route with CSRF disabled temporarily (as per request)
@auth_bp.route('/register', methods=['POST'])
@csrf.exempt
def register():
    username = request.form.get('reg_username')
    email = request.form.get('reg_email')
    password = request.form.get('reg_password')

    # Check for duplicates
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('auth.login'))

    if User.query.filter_by(email=email).first():
        flash('Email is already registered.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Registration failed: {str(e)}', 'danger')

    return redirect(url_for('auth.login'))

# ✅ Logout route
@auth_bp.route('/logout')
@login_required
def logout():
    if current_user.is_authenticated:
        activity = ActivityLog(
            user_id=current_user.username,
            action='User logged out',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        logout_user()
        flash('Logged out successfully.', 'success')

    return redirect(url_for('auth.login'))
