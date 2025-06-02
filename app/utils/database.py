from app import db
from app.models import User
from datetime import datetime

def init_db():
    """Initialize the database with default values"""
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            email='admin@example.com',  # ✅ Provide a valid email
            password_hash='Admin1!',  # ⚠️ Replace with actual hashed password
            role='admin',
            is_active=True,
            created_at=datetime.utcnow(),
            last_password_change=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
