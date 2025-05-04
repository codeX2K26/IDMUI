from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from reportlab.pdfgen import canvas
from io import BytesIO
from app.models import User, ActivityLog
from app import db

user_bp = Blueprint('user_management', __name__)

@user_bp.route('/users')
@login_required
def user_list():
    """
    Display the list of users. Only accessible to admins.
    """
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('service_management.dashboard'))
    
    users = User.query.all()
    return render_template('users/list.html', users=users)


@user_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """
    Create a new user. Only accessible to admins.
    """
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('service_management.dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('user_management.create_user'))
        
        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('User created successfully', 'success')
        return redirect(url_for('user_management.user_list'))
    
    return render_template('users/create.html')


@user_bp.route('/users/delete/<int:user_id>')
@login_required
def delete_user(user_id):
    """
    Delete a user. Only accessible to admins.
    """
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('service_management.dashboard'))
    
    user = User.query.get(user_id)
    if not user:
        flash('User not found', 'danger')
        return redirect(url_for('user_management.user_list'))

    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('user_management.user_list'))


@user_bp.route('/users/report')
@login_required
def generate_report():
    """
    Generate a PDF report of all users.
    Only accessible to admins.
    """
    if current_user.role != 'admin':
        flash('Access denied', 'danger')
        return redirect(url_for('service_management.dashboard'))

    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    # Header
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, "User Activity Report")
    
    # Table headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 780, "Username")
    p.drawString(300, 780, "Role")
    
    # User data
    y = 760
    p.setFont("Helvetica", 12)
    users = User.query.all()
    for user in users:
        p.drawString(100, y, user.username)
        p.drawString(300, y, user.role)
        y -= 20
    
    p.showPage()
    p.save()

    buffer.seek(0)
    response = make_response(buffer.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=user_report.pdf'
    return response
