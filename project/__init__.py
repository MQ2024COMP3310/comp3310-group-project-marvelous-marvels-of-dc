from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from pathlib import Path
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
login_manager = LoginManager() 
load_dotenv()

# init CSRF protection library
csrf = CSRFProtect() 

def create_app():
    app = Flask(__name__)
    csrf.init_app(app) # add csrf protection to the app

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    CWD = Path(os.path.dirname(__file__))
    app.config['UPLOAD_DIR'] = CWD / "uploads"

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login' 

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from .auth.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
