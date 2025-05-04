# app/utils/keystone_api.py
import requests
from flask import current_app
from requests.auth import HTTPBasicAuth

def keystone_request(method, endpoint, data=None):
    """
    Generic function to make API requests to the Keystone service.
    
    :param method: HTTP method (GET, POST, etc.)
    :param endpoint: Keystone API endpoint (e.g., '/status')
    :param data: Optional JSON payload for POST requests
    :return: JSON response or None in case of an error
    """
    try:
        response = requests.request(
            method,
            f"{current_app.config['KEYSTONE_URL']}{endpoint}",
            json=data,
            auth=HTTPBasicAuth(
                current_app.config['ADMIN_USER'],
                current_app.config['ADMIN_PASSWORD']
            ),
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.json() if response.content else {}
    except requests.RequestException as e:
        current_app.logger.error(f"Keystone API error ({method} {endpoint}): {e}")
        return None


def get_service_status():
    """
    Fetch the status of the Keystone service.
    
    :return: JSON response containing service status or {'active': False} on failure
    """
    response = keystone_request('GET', '/status')
    return response if response else {'active': False}


def manage_service(action):
    """
    Manage Keystone service actions (start, stop, restart).
    
    :param action: The action to perform ('start', 'stop', 'restart')
    :return: True if successful, False otherwise
    """
    valid_actions = {'start', 'stop', 'restart'}
    if action not in valid_actions:
        current_app.logger.warning(f"Invalid service action: {action}")
        return False
    return keystone_request('POST', f'/service/{action}') is not None


def keystone_auth(username, password):
    """
    Authenticate a user against the Keystone service.
    
    :param username: User's name
    :param password: User's password
    :return: True if authentication is successful, False otherwise
    """
    auth_data = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": username,
                        "domain": {"id": "default"},
                        "password": password
                    }
                }
            }
        }
    }

    try:
        response = requests.post(
            f"{current_app.config['KEYSTONE_URL']}/auth/tokens",
            json=auth_data,
            headers={'Content-Type': 'application/json'}
        )
        response.raise_for_status()
        return response.status_code == 201
    except requests.RequestException as e:
        current_app.logger.error(f"Authentication error for user {username}: {e}")
        return False
