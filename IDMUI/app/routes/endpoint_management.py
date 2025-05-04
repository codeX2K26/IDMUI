from flask import Blueprint, render_template, request, flash
from flask_login import login_required
from app.utils.keystone_auth import get_keystone_client

endpoint_bp = Blueprint('endpoint', __name__)

@endpoint_bp.route('/endpoints')
@login_required
def list_endpoints():
    keystone = get_keystone_client()
    services = keystone.services.list()
    endpoints = keystone.endpoints.list()
    return render_template('endpoints/list.html', 
                         services=services, endpoints=endpoints)

@endpoint_bp.route('/endpoints/create', methods=['POST'])
@login_required
def create_endpoint():
    service = request.form['service']
    interface = request.form['interface']
    url = request.form['url']
    
    keystone = get_keystone_client()
    keystone.endpoints.create(
        service=service,
        interface=interface,
        url=url,
        enabled=True
    )
    flash('Endpoint created successfully', 'success')
    return redirect(url_for('endpoint.list_endpoints'))