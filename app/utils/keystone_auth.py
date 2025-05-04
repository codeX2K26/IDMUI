from flask import current_app
from keystoneauth1 import identity, session
from keystoneclient.v3 import client

def get_keystone_admin_session():
    """
    Create an admin session using credentials from the app config.
    """
    auth = identity.Password(
        auth_url=current_app.config['KEYSTONE_AUTH_URL'],
        username=current_app.config['ADMIN_USER'],
        password=current_app.config['ADMIN_PASSWORD'],
        user_domain_name='Default',
        project_name='admin',
        project_domain_name='Default'
    )
    return session.Session(auth=auth)

def get_keystone_client(sess=None):
    """
    Return a Keystone client using the provided session (or admin session by default).
    """
    return client.Client(session=sess or get_keystone_admin_session())

def keystone_authenticate(username, password):
    """
    Authenticate a user against Keystone and return a token and project ID.
    """
    try:
        auth = identity.Password(
            auth_url=current_app.config['KEYSTONE_AUTH_URL'],
            username=username,
            password=password,
            user_domain_name='Default',
            project_name='admin',
            project_domain_name='Default'
        )
        sess = session.Session(auth=auth)
        return sess.get_token(), sess.get_project_id()
    except Exception as e:
        current_app.logger.error(f"Authentication failed: {e}")
        return None, None
