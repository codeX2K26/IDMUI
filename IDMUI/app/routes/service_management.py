from flask import Blueprint, render_template, flash
from flask_login import login_required
from app.utils.keystone_api import get_service_status, manage_service

service_bp = Blueprint('service_management', __name__)

@service_bp.route('/dashboard')
@login_required
def dashboard():
    status = get_service_status()
    return render_template('services/keystone_status.html', status=status)

@service_bp.route('/control/<action>')
@login_required
def service_control(action):
    result = manage_service(action)
    if result:
        flash(f'Service {action}ed successfully', 'success')
    else:
        flash(f'Failed to {action} service', 'danger')
    return redirect(url_for('service_management.dashboard'))