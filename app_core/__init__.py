import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from extensions import db, login_manager
from user import User


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')

load_dotenv(os.path.join(BASE_DIR, '.env'))


def create_app():
    app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
    CORS(app)

    # Secrets & configuration
    secret = os.environ.get('SECRET_KEY', 'minha_chave_secreta')
    app.config['SECRET_KEY'] = secret
    app.secret_key = secret
    app.config['database'] = os.environ.get('APP_DATABASE', 'default')

    # Database configuration
    uri = os.getenv("DATABASE_URL", 'sqlite:///users.db')
    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['GOOGLE_MAPS_API_KEY'] = os.environ.get('GOOGLE_MAPS_API_KEY')
    app.config.setdefault(
        'SOLID_PNG_ROOT',
        os.path.join(STATIC_DIR, 'SOLID_PRT_ASM', 'PNGS'),
    )

    db.init_app(app)
    Migrate(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'ui.login'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app_core.routes.ui import bp as ui_bp
    app.register_blueprint(ui_bp)

    @app.context_processor
    def inject_defaults():
        return {'current_year': datetime.utcnow().year}

    return app
