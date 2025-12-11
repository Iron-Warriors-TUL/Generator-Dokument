from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
import os
from app.services.data_loader import get_students, get_signers
from app.services.pdf_generator import generate_pdf, OUTPUT_DIR
from app.models import User
from flask_login import login_user, logout_user, current_user
from flask import redirect, url_for, flash

main = Blueprint("main", __name__)


@main.route("/")
@login_required
def dashboard():
    students = get_students()
    signers = get_signers()

    template_dir = "/app/latex_templates"
    try:
        templates = [f for f in os.listdir(template_dir) if f.endswith(".tex")]
    except FileNotFoundError:
        templates = []

    return render_template(
        "dashboard.html", students=students, signers=signers, templates=templates
    )


@main.route("/generate_custom", methods=["POST"])
@login_required
def generate_custom():
    student_id = int(request.form["student_id"])
    template_name = request.form["template_name"]

    ids = [
        int(request.form["signer_left"]),
        int(request.form["signer_mid"]),
        int(request.form["signer_right"]),
    ]

    all_students = get_students()
    all_signers = get_signers()

    student = next((s for s in all_students if s["id"] == student_id), None)

    selected_signers = []
    for sid in ids:
        signer = next((s for s in all_signers if s["id"] == sid), None)
        if signer:
            selected_signers.append(signer)

    if not student or len(selected_signers) != 3:
        return "Error", 404

    try:
        filename = generate_pdf(student, template_name, selected_signers)
        return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)
    except Exception as e:
        return str(e), 500


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        env_user = os.environ.get("ADMIN_USER", "admin")
        env_pass = os.environ.get("ADMIN_PASSWORD", "admin")

        if (
            request.form["username"] == env_user
            and request.form["password"] == env_pass
        ):
            login_user(User("admin"))
            return redirect(url_for("main.dashboard"))

        flash("Błędne dane")
    return render_template("login.html")


@main.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))
