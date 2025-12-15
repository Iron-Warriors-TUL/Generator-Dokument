from flask import Flask
from app.database import db_session, init_db
from app.views.auth import auth_bp
from app.views.dashboard import dashboard_bp
from app.views.admin import admin_bp
from app.models import User
from app.extensions import bcrypt, login_manager


def create_app():
    app = Flask(__name__)
    app.secret_key = "change_this_to_something_really_secret"

    init_db()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Zaloguj się, aby uzyskać dostęp."
    login_manager.init_app(app)

    bcrypt.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    return app
