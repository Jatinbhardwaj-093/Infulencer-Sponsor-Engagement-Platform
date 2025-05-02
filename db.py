from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

# Initialize extensions to be shared across the application
db = SQLAlchemy()
bcrypt = Bcrypt()
migrate = Migrate()
csrf = CSRFProtect()