from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import ActivityLog, User
from app.utils.keystone_auth import keystone_authenticate
from app import db, csrf
from werkzeug.security import generate_password_hash
from functools import wraps
from flask import abort

auth_bp = Blueprint('auth', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

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

# ✅ Disable CSRF for login only
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
            flash('Invalid credentials or Keystone error', 'danger')

    return render_template('auth/login.html')

# ✅ CSRF enabled for registration for security
@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form['reg_username']
    email = request.form['reg_email']
    password = request.form['reg_password']

    if User.query.filter_by(username=username).first():
        flash('Username already taken.', 'danger')
        return redirect(url_for('auth.login'))

    if User.query.filter_by(email=email).first():
        flash('Email already registered.', 'danger')
        return redirect(url_for('auth.login'))

    try:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
    except Exception as e:
        flash(f'Registration failed: {e}', 'danger')

    return redirect(url_for('auth.login'))

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
