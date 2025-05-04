from flask import Blueprint, render_template
from flask_login import login_required
from app.utils.keystone_auth import get_keystone_client

token_bp = Blueprint('token', __name__)

@token_bp.route('/tokens')
@login_required
def list_tokens():
    keystone = get_keystone_client()
    tokens = keystone.tokens.list()
    return render_template('tokens/list.html', tokens=tokens)

@token_bp.route('/tokens/revoke/<token_id>', methods=['POST'])
@login_required
def revoke_token(token_id):
    keystone = get_keystone_client()
    keystone.tokens.revoke(token_id)
    return '', 204