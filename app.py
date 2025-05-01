from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect
import os
import logging
from datetime import datetime

# Initialize extensions first without the app
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()

def create_app(config_object='config.active_config'):
    """Application factory pattern for Flask app"""
    app = Flask(__name__)
    
    # Configure the app
    app.config.from_object(config_object)
    
    # Initialize extensions with the app
    db.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    csrf.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Setup logging
    setup_logging(app)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    with app.app_context():
        # Import models to ensure they're registered with SQLAlchemy
        from models import Admin, Influencer, Sponsor, Campaign, InfluencerAdRequest, SponsorRequest, Img
        from utils.notifications import Notification
        
        # Create database tables if they don't exist
        db.create_all()
        
        # Import and register blueprints
        from routes import register_routes
        from api import register_api_routes
        
        register_routes(app)
        register_api_routes(app)
        
        # Register error handlers
        register_error_handlers(app)
        
        # Add context processors
        register_context_processors(app)
        
        return app

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

def register_error_handlers(app):
    """Register error handlers for the application"""
    
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401

def register_context_processors(app):
    """Register context processors for the application"""
    
    @app.context_processor
    def inject_user():
        from utils.security import get_current_user, get_user_type
        return {
            'current_user': get_current_user(),
            'user_type': get_user_type()
        }
    
    @app.context_processor
    def inject_notification_count():
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

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)