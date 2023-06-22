import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Create the global objects
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
moment = Moment()


def create_app(config_class=Config):
    # Create and configure the app
    app = Flask(__name__)
    app.config.from_object(config_class)

    # init all the packages
    db.init_app(app)
    migrate.init_app(app, db)
    Bootstrap5(app)
    login.init_app(app)
    login.login_view = 'auth.login'
    login.login_message = 'Please log in to access this page.'
    moment.init_app(app)

    from errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from main import bp as main_bp
    app.register_blueprint(main_bp)

    from auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from admin import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    @app.before_request
    def before_request():
        if current_user.is_authenticated:
            current_user.last_seen = datetime.utcnow()
            db.session.commit()

    return app


# noinspection PyUnresolvedReferences
import errors, models

if __name__ == '__main__':
    application = create_app()
