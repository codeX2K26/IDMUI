from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    socketio.init_app(app)

    # Configure Flask-Login
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'danger'

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except:
            return None

    # Logging setup
    if not app.debug:
        file_handler = RotatingFileHandler('idmui.log', maxBytes=1024 * 1024, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.service_management import service_bp
    from app.routes.user_management import user_bp
    from app.routes.project_management import project_bp
    from app.routes.endpoint_management import endpoint_bp
    from app.routes.domain_management import domain_bp
    from app.routes.database_management import database_bp
    from app.routes.configuration_management import config_bp
    from app.routes.metrics import metrics_bp
    from app.routes.token_management import token_bp
    from app.routes.group_management import group_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(endpoint_bp)
    app.register_blueprint(domain_bp)
    app.register_blueprint(database_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(metrics_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(group_bp)

    # Root route - Login page
    @app.route('/')
    def root():
        return render_template('auth/login.html')

    # Fallback dashboard route for testing
    @app.route('/dashboard')
    def dashboard_fallback():
        return "<h3>Test Dashboard Route Active</h3>"

    with app.app_context():
        try:
            from app.models import ActivityLog
            db.create_all()
            app.logger.info("Database tables created successfully")

            # Optional: initialize default data
            from app.utils.database import init_db
            init_db()

        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise

        # Register custom Jinja filter
        @app.template_filter('datetimeformat')
        def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
            return value.strftime(format) if value else ""

    # Security Headers
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    return app

__all__ = ['create_app', 'socketio']
