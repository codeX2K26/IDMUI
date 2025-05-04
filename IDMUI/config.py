import os
from datetime import timedelta

class Config:
    # ========================
    # Security Configuration
    # ========================
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
    WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY', os.urandom(32))
    SESSION_COOKIE_NAME = 'idmui_session'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    
    # ========================
    # Database Configuration
    # ========================
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://idmui_user:SecurePass123!@localhost/idmui_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # ========================
    # Keystone Configuration
    # ========================
    KEYSTONE_AUTH_URL = os.environ.get('KEYSTONE_AUTH_URL', 'http://192.168.56.101:5000/v3')
    KEYSTONE_ADMIN_USER = os.environ.get('KEYSTONE_ADMIN_USER', 'admin')
    KEYSTONE_ADMIN_PASSWORD = os.environ.get('KEYSTONE_ADMIN_PASSWORD', '')
    KEYSTONE_TIMEOUT = 15  # seconds
    KEYSTONE_TOKEN_EXPIRATION = 3600  # 1 hour

    # ========================
    # Application Security
    # ========================
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_SALT', 'security-salt-123')
    RATE_LIMIT = '500/day;100/hour;20/minute'

    # ========================
    # File Uploads & Backups
    # ========================
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/var/uploads/idmui'
    BACKUP_DIR = '/var/backups/idmui'
    ALLOWED_EXTENSIONS = {'sql', 'bak'}

    # ========================
    # Logging Configuration
    # ========================
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = '/var/log/idmui/app.log'

    # ========================
    # Email Configuration
    # ========================
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USER')
    MAIL_PASSWORD = os.environ.get('MAIL_PASS')
    ADMIN_EMAIL = 'admin@idmui.local'

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_HTTPONLY = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True