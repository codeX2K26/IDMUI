from flask import Blueprint, render_template, request, flash
from flask_login import login_required
import configparser
import os

config_bp = Blueprint('config', __name__)

CONFIG_PATH = '/etc/keystone/keystone.conf'

@config_bp.route('/config')
@login_required
def view_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return render_template('config/view.html', config=config)

@config_bp.route('/config/update', methods=['POST'])
@login_required
def update_config():
    section = request.form['section']
    key = request.form['key']
    value = request.form['value']
    
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    
    if not config.has_section(section):
        config.add_section(section)
    
    config.set(section, key, value)
    
    with open(CONFIG_PATH, 'w') as configfile:
        config.write(configfile)
    
    flash('Configuration updated successfully', 'success')
    return redirect(url_for('config.view_config'))