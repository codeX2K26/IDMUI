from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
import logging
from logging.handlers import RotatingFileHandler
from flask_wtf.csrf import CSRFProtect

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'danger'
    
    # Set up logging
    if not app.debug:
        file_handler = RotatingFileHandler(
            'idmui.log',
            maxBytes=1024 * 1024,
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    # Register blueprints
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

    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
            
            # Initialize default data if needed
            from app.utils.database import init_db
            init_db()
            
        except Exception as e:
            app.logger.error(f"Database initialization failed: {str(e)}")
            raise

        # Register custom Jinja filters
        @app.template_filter('datetimeformat')
        def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
            if value is None:
                return ""
            return value.strftime(format)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    return app
