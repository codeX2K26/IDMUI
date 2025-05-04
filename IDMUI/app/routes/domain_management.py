from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.utils.keystone_auth import get_keystone_client

domain_bp = Blueprint('domain', __name__)

@domain_bp.route('/domains')
@login_required
def list_domains():
    keystone = get_keystone_client()
    domains = keystone.domains.list()
    return render_template('domains/list.html', domains=domains)

@domain_bp.route('/domains/create', methods=['POST'])
@login_required
def create_domain():
    name = request.form['name']
    description = request.form['description']
    
    keystone = get_keystone_client()
    keystone.domains.create(
        name=name,
        description=description,
        enabled=True
    )
    flash('Domain created successfully', 'success')
    return redirect(url_for('domain.list_domains'))