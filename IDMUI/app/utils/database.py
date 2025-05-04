from app import db
from app.models import User

def init_db():
    """Initialize the database with default values"""
    db.create_all()
    
    # Create admin user if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash='hashed_password',  # Use proper password hashing
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()