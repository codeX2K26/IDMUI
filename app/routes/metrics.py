from flask import Blueprint, jsonify
from flask_login import login_required
from app.utils.keystone_auth import get_keystone_client

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/stats/users')
@login_required
def user_stats():
    keystone = get_keystone_client()
    users = keystone.users.list()
    return jsonify({
        'total_users': len(users),
        'active_users': len([u for u in users if u.enabled])
    })

@metrics_bp.route('/stats/projects')
@login_required
def project_stats():
    keystone = get_keystone_client()
    projects = keystone.projects.list()
    return jsonify({
        'total_projects': len(projects),
        'domains': len({p.domain_id for p in projects})
    })