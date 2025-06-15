from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import ActivityLog, User
from app.utils.keystone_auth import keystone_authenticate
from app import db, csrf
from functools import wraps
from flask import abort

auth_bp = Blueprint('auth', __name__)

# RBAC: Only allow admin users
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

# ✅ LOGIN (Keystone)
@auth_bp.route('/login', methods=['GET', 'POST'])
@csrf.exempt
def login():
    if request.method == 'POST':
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
            flash('Invalid Keystone credentials', 'danger')

    return render_template('auth/login.html')

# ✅ LOGOUT
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

# ✅ REGISTER
@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form['reg_username']
    email = request.form['reg_email']
    password = request.form['reg_password']

    if User.query.filter_by(username=username).first():
        flash('Username already exists', 'danger')
        return redirect(url_for('auth.login'))

    new_user = User(username=username, email=email)
    new_user.set_password(password)  # Must implement this in User model
    db.session.add(new_user)
    db.session.commit()

    flash('Registration successful. Please log in.', 'success')
    return redirect(url_for('auth.login'))
