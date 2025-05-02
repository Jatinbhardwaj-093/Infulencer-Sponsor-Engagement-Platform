"""
Main application file for Influencer Engagement Platform
"""
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import os
import logging
from datetime import datetime
import sys

# Import db and extensions from db.py
from db import db, bcrypt, migrate, csrf

def create_app(config_object='config.active_config'):
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object(config_object)
    
    # Register error handlers first so they're available during initialization
    register_error_handlers(app)
    
    # Ensure required directories exist before doing anything else
    setup_directories(app)
    
    # Setup logging
    setup_logging(app)
    
    # Initialize extensions
    initialize_extensions(app)
    
    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        import_models()
        
        # Create database tables if they don't exist
        try:
            # Check database file and directory
            db_path = app.config['SQLALCHEMY_DATABASE_URI']
            if db_path.startswith('sqlite:///'):
                db_file = db_path.replace('sqlite:///', '')
                db_dir = os.path.dirname(db_file)
                
                # Ensure database directory exists
                os.makedirs(db_dir, exist_ok=True)
                app.logger.info(f"Ensuring database directory exists: {db_dir}")
                
                # Check if we can write to the directory
                if not os.access(db_dir, os.W_OK):
                    app.logger.warning(f"No write permission for database directory: {db_dir}")
                    print(f"WARNING: No write permission for database directory: {db_dir}", file=sys.stderr)
                    # Try to fix permissions if possible
                    try:
                        os.chmod(db_dir, 0o777)  # Set directory to be writable by everyone
                        app.logger.info(f"Updated directory permissions for: {db_dir}")
                    except Exception as perm_e:
                        app.logger.error(f"Could not update directory permissions: {str(perm_e)}")
                
                # If database file exists, check its permissions
                if os.path.exists(db_file):
                    if not os.access(db_file, os.W_OK):
                        app.logger.warning(f"No write permission for database file: {db_file}")
                        # Try to fix permissions if possible
                        try:
                            os.chmod(db_file, 0o666)  # Set file to be writable by everyone
                            app.logger.info(f"Updated file permissions for: {db_file}")
                        except Exception as perm_e:
                            app.logger.error(f"Could not update file permissions: {str(perm_e)}")
            
            # Create database tables
            db.create_all()
            app.logger.info("Database tables created successfully")
            
        except Exception as e:
            app.logger.error(f"Database initialization error: {str(e)}")
            print(f"Error: {str(e)}", file=sys.stderr)
            # Print more information about the database path for debugging
            print(f"Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}", file=sys.stderr)
        
        # Import and register blueprints
        from routes import register_routes
        from api import register_api_routes
        
        register_routes(app)
        register_api_routes(app)
        
        # Register context processors
        register_context_processors(app)
        
        # Setup custom jinja filters
        register_jinja_filters(app)
        
        return app

def initialize_extensions(app):
    """Initialize Flask extensions"""
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

def import_models():
    """Import models to register them with SQLAlchemy"""
    from models import Admin, Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, Img, Notification

def setup_logging(app):
    """Configure logging for the application"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
        
    log_file = os.path.join('logs', f"{datetime.now().strftime('%Y-%m-%d')}.log")
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Influencer Engagement Platform startup')

def setup_directories(app):
    """Ensure required directories exist"""
    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)
    
    # Ensure uploads directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Ensure logs directory exists with proper permissions
    logs_dir = app.config.get('LOG_FOLDER', 'logs')
    os.makedirs(logs_dir, exist_ok=True)

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 error: {request.url if 'request' in globals() else 'Unknown URL'}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 error: {str(e)}")
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f"403 error: {request.url if 'request' in globals() else 'Unknown URL'}")
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401
    
    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return render_template('errors/500.html'), 500

def register_context_processors(app):
    """Register context processors for the application"""
    
    @app.context_processor
    def inject_user():
        from flask import session
        from utils.security import get_current_user, get_user_type
        return {
            'current_user': get_current_user(),
            'user_type': get_user_type()
        }
    
    @app.context_processor
    def inject_notification_count():
        from flask import session
        from utils.security import get_current_user, get_user_type, is_authenticated
        from utils.notifications import get_unread_count
        
        if not is_authenticated():
            return {'unread_notifications': 0}
            
        user = get_current_user()
        user_type = get_user_type()
        
        if not user:
            return {'unread_notifications': 0}
        
        if user_type == 'admin':
            user_id = user.admin_id
        elif user_type == 'influencer':
            user_id = user.influencer_id
        elif user_type == 'sponsor':
            user_id = user.sponsor_id
        else:
            return {'unread_notifications': 0}
            
        unread_count = get_unread_count(user_id, user_type)
        return {'unread_notifications': unread_count}

def register_jinja_filters(app):
    """Register custom Jinja filters"""
    
    @app.template_filter('datetime')
    def format_datetime(value, format='%Y-%m-%d %H:%M'):
        """Format a datetime object to string"""
        if value is None:
            return ''
        return value.strftime(format)
    
    @app.template_filter('currency')
    def format_currency(value):
        """Format a number as currency"""
        if value is None:
            return '$0.00'
        return f"${float(value):,.2f}"

# Create the app instance - for direct flask run
app = create_app()

# Import error handlers to register them
from flask import request

if __name__ == '__main__':
    app.run(debug=True)