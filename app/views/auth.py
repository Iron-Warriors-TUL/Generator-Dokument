from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.extensions import bcrypt

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard.index"))

        flash("Błędny login lub hasło", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth_bp.route("/login/ms")
def login_ms():
    redirect_uri = url_for("auth.authorize_ms", _external=True)
    return oauth.microsoft.authorize_redirect(redirect_uri)


@auth_bp.route("/authorize/ms")
def authorize_ms():
    token = oauth.microsoft.authorize_access_token()
    user_info = token.get("userinfo")

    if not user_info:
        flash("Błąd autoryzacji Microsoft.", "danger")
        return redirect(url_for("auth.login"))
    user = User.query.filter_by(username=user_info["email"]).first()
    if not user:
        flash(
            "Użytkownik nie istnieje w systemie. Skontaktuj się z administratorem.",
            "warning",
        )
        return redirect(url_for("auth.login"))

    login_user(user)
    return redirect(url_for("dashboard.index"))
