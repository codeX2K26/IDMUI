from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.utils.keystone_auth import get_keystone_client

project_bp = Blueprint('project', __name__)

@project_bp.route('/projects')
@login_required
def list_projects():
    keystone = get_keystone_client()
    projects = keystone.projects.list()
    return render_template('projects/list.html', projects=projects)

@project_bp.route('/projects/create', methods=['POST'])
@login_required
def create_project():
    name = request.form['name']
    description = request.form['description']
    domain = request.form['domain']
    
    keystone = get_keystone_client()
    keystone.projects.create(
        name=name,
        domain=domain,
        description=description,
        enabled=True
    )
    flash('Project created successfully', 'success')
    return redirect(url_for('project.list_projects'))