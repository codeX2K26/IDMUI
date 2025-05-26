from app import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
import re

class User(db.Model, UserMixin):
    __tablename__ = 'users'  # FIXED: double underscores
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(64), default='user', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    last_password_change = db.Column(db.DateTime)

    # Relationship
    activities = db.relationship('ActivityLog', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        """Hash and set password with complexity check"""
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters long")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")
            
        self.password_hash = generate_password_hash(password)
        self.last_password_change = datetime.utcnow()

    def check_password(self, password):
        """Verify password with timing attack protection"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'  # FIXED: double underscores
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(512), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

    # Relationship
    user = db.relationship('User', back_populates='activities')

    def __repr__(self):
        return f'<ActivityLog {self.action} at {self.timestamp}>'


# Indexes
db.Index('ix_users_email', User.email, unique=True)
db.Index('ix_activity_logs_timestamp', ActivityLog.timestamp)

# Event listener for password changes
@event.listens_for(User.password_hash, 'set')
def password_changed_listener(target, value, oldvalue, initiator):
    target.last_password_change = datetime.utcnow()
