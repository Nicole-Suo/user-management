from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(config_class)

    CORS(
        app,
        resources={r"/api/*": {"origins": ["http://localhost:5173", "http://127.0.0.1:5173"]}},
        supports_credentials=True,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    login.login_view = 'auth.login'

    # For API requests we should return JSON 401 instead of redirecting to the
    # HTML login page. Flask-Login by default redirects unauthenticated
    # requests to `login_view`, which breaks fetch/XHR (it causes a GET to the
    # login route and a 405). Register an unauthorized handler to return a
    # JSON response for API paths.
    @login.unauthorized_handler
    def unauthorized_callback():
        from flask import request, jsonify, redirect, url_for

        if request.path.startswith('/api/'):
            return jsonify({'error': 'unauthenticated'}), 401
        return redirect(url_for('auth.login', next=request.path))

    from app import auth, models, routes

    app.register_blueprint(auth.bp)
    app.register_blueprint(routes.bp)

    return app
