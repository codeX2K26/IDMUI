from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.utils.keystone_auth import get_keystone_client

group_bp = Blueprint('group', __name__)

@group_bp.route('/groups')
@login_required
def list_groups():
    keystone = get_keystone_client()
    groups = keystone.groups.list()
    return render_template('groups/list.html', groups=groups)

@group_bp.route('/groups/create', methods=['POST'])
@login_required
def create_group():
    name = request.form['name']
    description = request.form['description']
    domain = request.form['domain']
    
    keystone = get_keystone_client()
    keystone.groups.create(
        name=name,
        domain=domain,
        description=description
    )
    flash('Group created successfully', 'success')
    return redirect(url_for('group.list_groups'))