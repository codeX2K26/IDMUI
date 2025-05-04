from flask import Blueprint, send_file
from flask_login import login_required
import subprocess
from io import BytesIO
from datetime import datetime

db_bp = Blueprint('database', __name__)

@db_bp.route('/backup')
@login_required
def backup_database():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"idmui_backup_{timestamp}.sql"
    
    # Execute mysqldump command
    proc = subprocess.Popen(
        ['mysqldump', '-u', 'idmui_user', '-pSecurePass123!', 'idmui_db'],
        stdout=subprocess.PIPE
    )
    dump = BytesIO(proc.stdout.read())
    
    return send_file(
        dump,
        as_attachment=True,
        download_name=filename,
        mimetype='application/sql'
    )

@db_bp.route('/restore', methods=['POST'])
@login_required
def restore_database():
    if 'backup_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('some_route'))
    
    file = request.files['backup_file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('some_route'))
    
    # Execute mysql restore
    proc = subprocess.Popen(
        ['mysql', '-u', 'idmui_user', '-pSecurePass123!', 'idmui_db'],
        stdin=subprocess.PIPE
    )
    proc.stdin.write(file.read())
    proc.stdin.close()
    
    flash('Database restored successfully', 'success')
    return redirect(url_for('database.backup_database'))