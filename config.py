"""
Configuration settings for the Influencer Engagement Platform
"""
import os
import secrets
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get the absolute path to the project directory - more reliable method
PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(PROJECT_DIR, 'instance')
if not os.path.exists(INSTANCE_DIR):
    os.makedirs(INSTANCE_DIR, exist_ok=True)

def get_db_uri():
    """Helper function to handle database URI paths properly"""
    db_uri = os.environ.get('DATABASE_URI')
    
    if not db_uri:
        # Default to project root if no DATABASE_URI is specified
        return f'sqlite:///{os.path.join(PROJECT_DIR, "influencer_platform.db")}'
    
    if db_uri.startswith('sqlite:///./'):
        # Handle explicit relative path from project root
        relative_path = db_uri.replace('sqlite:///./','')
        return f'sqlite:///{os.path.join(PROJECT_DIR, relative_path)}'
    elif db_uri.startswith('sqlite:///') and not db_uri.startswith('sqlite:////'):
        # Handle standard relative path
        relative_path = db_uri.replace('sqlite:///','')
        return f'sqlite:///{os.path.join(PROJECT_DIR, relative_path)}'
    else:
        # Use as is (absolute paths or non-SQLite databases)
        return db_uri

# Base configuration class
class Config:
    """Base configuration class with settings common to all environments"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    DEBUG = False
    TESTING = False
    
    # Database settings - Using the helper function to ensure correct path resolution
    SQLALCHEMY_DATABASE_URI = get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(PROJECT_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'mp4', 'mov'}
    
    # Logging settings
    LOG_FOLDER = os.path.join(PROJECT_DIR, 'logs')
    LOG_LEVEL = 'INFO'
    
    # Email settings (for future use)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    
    # API settings
    API_RATE_LIMIT = '100 per minute'
    
    # Security settings
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_NUMBER = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    # Admin settings
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@example.com')
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')  # Only for dev, override in prod

# Development configuration
class DevelopmentConfig(Config):
    """Configuration for development environment"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = 'DEBUG'

# Testing configuration
class TestingConfig(Config):
    """Configuration for testing environment"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

# Production configuration
class ProductionConfig(Config):
    """Configuration for production environment"""
    # Ensure SECRET_KEY is properly set in production
    if not os.environ.get('SECRET_KEY'):
        # Instead of raising error, log a warning and use a fallback
        print("WARNING: SECRET_KEY environment variable not set. Using a randomly generated key.")
        # This allows the app to start but with a warning
    
    # Allow SQLite as fallback in production if DATABASE_URI is not set
    if not os.environ.get('DATABASE_URI'):
        print("WARNING: DATABASE_URI environment variable not set. Using SQLite as fallback.")
        print("For production deployments, it's recommended to use PostgreSQL or MySQL.")
        # This uses the default from the Config class
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=14)
    
    # Production logging
    LOG_LEVEL = 'ERROR'

# Get config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Load the correct configuration based on FLASK_ENV environment variable
active_config = config.get(os.environ.get('FLASK_ENV', 'default'))


