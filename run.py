from app import create_app, socketio
from app.utils.database import init_db
import logging
import os

app = create_app()

def initialize_application():
    with app.app_context():
        try:
            # Initialize database with error handling
            init_db()
            app.logger.info("Database initialization completed successfully")
            
            # Add any other pre-startup tasks here
            from app.utils.keystone_api import verify_keystone_connection
            if not verify_keystone_connection():
                raise RuntimeError("Failed to connect to Keystone service")
                
        except Exception as e:
            app.logger.error(f"Application initialization failed: {str(e)}")
            raise

if _name_ == '_main_':
    # Configure logging before starting
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('idmui.log'),
            logging.StreamHandler()
        ]
    )
    
    # Perform initialization
    initialize_application()
    
    # Get port from environment variable or use default
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Run application with Socket.IO support
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=app.debug,
        use_reloader=False if app.config.get('TESTING') else True
    )