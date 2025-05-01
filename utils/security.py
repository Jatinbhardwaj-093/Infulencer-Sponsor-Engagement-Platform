import os
import secrets
import functools
from flask import session, redirect, url_for, flash, request, abort
from models import Influencer, Sponsor, Admin, db
from werkzeug.utils import secure_filename
import re
import bleach
from datetime import datetime
import string
from functools import wraps

def is_authenticated():
    """Check if any user type is logged in"""
    return 'admin_id' in session or 'influencer_id' in session or 'sponsor_id' in session

def get_user_type():
    """Get the type of the current logged-in user"""
    if 'admin_id' in session:
        return 'admin'
    elif 'influencer_id' in session:
        return 'influencer'
    elif 'sponsor_id' in session:
        return 'sponsor'
    else:
        return None

def get_current_user():
    """Get the current logged-in user object"""
    user_type = get_user_type()
    
    if user_type == 'admin':
        return Admin.query.get(session.get('admin_id'))
    elif user_type == 'influencer':
        return Influencer.query.get(session.get('influencer_id'))
    elif user_type == 'sponsor':
        return Sponsor.query.get(session.get('sponsor_id'))
    else:
        return None

def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Please login to access this page', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated() or get_user_type() != 'admin':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def influencer_required(f):
    """Decorator to require influencer login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated() or get_user_type() != 'influencer':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def sponsor_required(f):
    """Decorator to require sponsor login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated() or get_user_type() != 'sponsor':
            flash('You do not have permission to access this page', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

def logout_user():
    """Clear all user sessions."""
    session.pop('admin_id', None)
    session.pop('influencer_id', None)
    session.pop('sponsor_id', None)
    session.pop('user_id', None)
    session.pop('user_type', None)

def sanitize_input(text):
    """Sanitize user input to prevent XSS attacks"""
    if not text:
        return text
        
    # Replace potentially dangerous characters
    text = re.sub(r'<', '&lt;', text)
    text = re.sub(r'>', '&gt;', text)
    text = re.sub(r'"', '&quot;', text)
    text = re.sub(r"'", '&#39;', text)
    
    return text

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """Validate username format."""
    pattern = r'^[a-zA-Z0-9_-]{3,20}$'
    return re.match(pattern, username) is not None

def validate_password_strength(password):
    """
    Validate password strength
    Returns a tuple (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
        
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
        
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
        
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
        
    return True, "Password is strong"

def validate_image_file(file):
    """Validate that file is a safe image."""
    if not file:
        return False
    
    # Check if the file extension is allowed
    allowed_extensions = {'jpg', 'jpeg', 'png', 'gif'}
    filename = file.filename.lower()
    
    if not '.' in filename or filename.rsplit('.', 1)[1] not in allowed_extensions:
        return False
    
    # Check if the content type is an allowed image type
    allowed_mimetypes = {'image/jpeg', 'image/png', 'image/gif'}
    if file.content_type not in allowed_mimetypes:
        return False
    
    return True

def handle_file_upload(file, upload_folder, allowed_extensions=None):
    """
    Handle secure file upload
    Returns (success, filename or error_message)
    """
    if file.filename == '':
        return False, "No file selected"
        
    if not allowed_file(file.filename, allowed_extensions):
        return False, "File type not allowed"
    
    # Generate a secure random filename to prevent path traversal attacks
    original_filename = secure_filename(file.filename)
    extension = os.path.splitext(original_filename)[1]
    random_string = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    filename = random_string + extension
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    
    return True, filename

def allowed_file(filename, allowed_extensions):
    """Check if file extension is allowed"""
    if allowed_extensions is None:
        # Default to common image formats if no extensions specified
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_csrf_token():
    """Generate a CSRF token for forms"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

def validate_csrf_token(token):
    """Validate a CSRF token"""
    if token != session.get('_csrf_token'):
        abort(403)  # Forbidden
    return True

def create_activity_log(user_id, user_type, action, details=None):
    """Log user activity for auditing purposes"""
    from datetime import datetime
    
    class ActivityLog(db.Model):
        """Model for activity logging"""
        __tablename__ = 'activity_logs'
        
        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, nullable=False)
        user_type = db.Column(db.String(20), nullable=False)
        action = db.Column(db.String(100), nullable=False)
        details = db.Column(db.Text)
        ip_address = db.Column(db.String(45))
        user_agent = db.Column(db.String(255))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    log = ActivityLog(
        user_id=user_id,
        user_type=user_type,
        action=action,
        details=details,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string if request.user_agent else None
    )
    
    db.session.add(log)
    db.session.commit()
    
    return log.id

def log_activity(user_id, user_type, action, details=None):
    """Log user activity for audit purposes."""
    # This could be expanded to write to a database or log file
    timestamp = datetime.utcnow()
    print(f"[{timestamp}] {user_type} (ID: {user_id}) {action} - {details}")