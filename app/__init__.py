from flask import Flask
from flask_login import LoginManager
from .models import User


def create_app():
    app = Flask(__name__)

    # Keep your secret key
    app.secret_key = "change_this_to_something_secret"

    # Initialize Login Manager
    login_manager = LoginManager()
    login_manager.login_view = (
        "main.login"  # Redirects to 'login' function in 'main' blueprint
    )
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == "admin":
            return User(user_id)
        return None

    # Register Blueprints
    from .routes import main

    app.register_blueprint(main)

    return app
