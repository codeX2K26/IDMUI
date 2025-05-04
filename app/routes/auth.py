from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import ActivityLog
from app.utils.keystone_auth import keystone_authenticate
from app import db

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
    """
    A temporary user class to store Keystone authentication details
    and work with Flask-Login.
    """
    def __init__(self, token, project_id, username):
        self.token = token
        self.project_id = project_id
        self.username = username
        self.is_authenticated = True
        self.is_active = True
        self.is_anonymous = False

    def get_id(self):
        return f"{self.username}|{self.token}|{self.project_id}"


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login using Keystone authentication.
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate with Keystone
        token, project_id = keystone_authenticate(username, password)
        if token:
            user = KeystoneUser(token, project_id, username)
            login_user(user)

            # Log user login activity
            activity = ActivityLog(
                user_id=username,  # Using username as a reference since Keystone doesn't have local DB users
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


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Handle user logout and log the activity.
    """
    if current_user.is_authenticated:
        # Log user logout activity
        activity = ActivityLog(
            user_id=current_user.username,  # Store username since Keystone users aren't in our local DB
            action='User logged out',
            ip_address=request.remote_addr
        )
        db.session.add(activity)
        db.session.commit()

        logout_user()
        flash('You have been logged out', 'success')

    return redirect(url_for('auth.login'))
