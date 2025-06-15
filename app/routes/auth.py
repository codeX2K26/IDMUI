from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import ActivityLog, User
from app.utils.keystone_auth import keystone_authenticate
from werkzeug.security import generate_password_hash
from app import db, csrf
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Role-Based Access Control (RBAC) Decorator for Admin Access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

class KeystoneUser:
    """A temporary user class to store Keystone authentication details and work with Flask-Login."""
    def __init__(self, token, project_id, username):
        self.token = token
        self.project_id = project_id
        self.username = username
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return f"{self.username}|{self.token}|{self.project_id}"

# ✅ Login route with CSRF exempted
@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Try Keystone authentication first
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

        # If Keystone fails, try local DB auth
        local_user = User.query.filter_by(username=username).first()
        if local_user and local_user.check_password(password):
            login_user(local_user)

            activity = ActivityLog(
                user_id=local_user.username,
                action='User logged in (local DB)',
                ip_address=request.remote_addr
            )
            db.session.add(activity)
            db.session.commit()

            flash('Local login successful.', 'success')
            return redirect(url_for('service_management.dashboard'))

        flash('Invalid credentials.', 'danger')

    return render_template('auth/login.html')

# ✅ Registration route (CSRF enabled)
@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('reg_username')
    password = request.form.get('reg_password')
    email = request.form.get('reg_email')

    if not username or not password or not email:
        flash("All fields are required.", "danger")
        return redirect(url_for('auth.login'))

    if User.query.filter_by(username=username).first():
        flash("Username already exists.", "warning")
        return redirect(url_for('auth.login'))

    new_user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password)
    )
    db.session.add(new_user)
    db.session.commit()

    flash("Registration successful. Please log in.", "success")
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
        flash('You have been logged out', 'success')

    return redirect(url_for('auth.login'))
