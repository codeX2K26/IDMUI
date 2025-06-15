from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.keystone_api import get_service_status, manage_service

service_bp = Blueprint('service_management', __name__)

@service_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        status = get_service_status()
        return render_template('services/keystone_status.html', status=status)
    except Exception as e:
        flash(f"Error loading dashboard: {e}", "danger")
        return "<h3>✅ Logged in, but dashboard error. Please check keystone_status.html or service call.</h3>"

@service_bp.route('/control/<action>')
@login_required
def service_control(action):
    result = manage_service(action)
    if result:
        flash(f'Service {action}ed successfully', 'success')
    else:
        flash(f'Failed to {action} service', 'danger')
    return redirect(url_for('service_management.dashboard'))
