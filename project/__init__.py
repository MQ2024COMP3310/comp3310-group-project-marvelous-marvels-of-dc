# Importing necessary libraries and modules.
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from pathlib import Path
from dotenv import load_dotenv  # For loading environment variables.
from flask_wtf.csrf import CSRFProtect  # For CSRF protection.

# Initialize SQLAlchemy so we can use it later in our models.
db = SQLAlchemy()
login_manager = LoginManager()
load_dotenv()  # Load environment variables from a .env file.

# Initialize CSRF protection.
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    csrf.init_app(app)  # Add CSRF protection to the app.

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # Set the secret key from environment variables.
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Database URI for SQLAlchemy.
    CWD = Path(os.path.dirname(__file__))
    app.config['UPLOAD_DIR'] = CWD / "uploads"  # Set the upload directory.
    
    # Initialize SQLAlchemy with the app.
    db.init_app(app)

    # Add login manager to the app for user authentication.
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Specifies the view to redirect to when the user needs to log in.

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))  # Reload the user object from the user ID stored in the session.

    # Blueprint for auth routes in our app.
    from .auth.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # Blueprint for non-auth parts of app.
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app  # Return the Flask app instance.