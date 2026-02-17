import os
from flask import Flask
from app.database import db_session, init_db
from app.views.auth import auth_bp
from app.views.dashboard import dashboard_bp
from app.views.admin import admin_bp
from app.models import User
from app.extensions import bcrypt, login_manager, oauth


def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv(
        "FLASK_SECRET_KEY", "fallback-if-not-set-but-use-env-in-prod"
    )

    init_db()

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db_session.remove()

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Zaloguj się, aby uzyskać dostęp."
    login_manager.init_app(app)

    bcrypt.init_app(app)
    oauth.init_app(app)
    ms_client_id = os.getenv("MS_CLIENT_ID")
    ms_client_secret = os.getenv("MS_CLIENT_SECRET")
    ms_tenant_id = os.getenv("MS_TENANT_ID", "common")

    oauth.register(
        name="microsoft",
        client_id=ms_client_id,
        client_secret=ms_client_secret,
        server_metadata_url=f"https://login.microsoftonline.com/{ms_tenant_id}/v2.0/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    return app
