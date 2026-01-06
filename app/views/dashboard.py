import os
from flask import Blueprint, render_template, request, send_file, current_app
from flask_login import login_required
from app.models import Student, Signer
from app.services.pdf_generator import generate_pdf, OUTPUT_DIR

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    students = Student.query.all()
    signers = Signer.query.all()
    template_dir = os.path.join(current_app.root_path, "latex_templates")
    try:
        # Pobieramy szablony, ignorując plik bazowy
        templates = [
            f
            for f in os.listdir(template_dir)
            if f.endswith(".tex") and f != "base.tex"
        ]
    except FileNotFoundError:
        templates = []
    return render_template(
        "dashboard.html", students=students, signers=signers, templates=templates
    )


@dashboard_bp.route("/generate_custom", methods=["POST"])
@login_required
def generate_custom():
    student_id = request.form.get("student_id")
    template_name = request.form.get("template_name")

    role_description = request.form.get("role_description", "")
    achievements_list = request.form.getlist("achievements[]")
    achievements_list = [a.strip() for a in achievements_list if a.strip()]

    signer_ids = [
        request.form.get("signer_left"),
        request.form.get("signer_mid"),
        request.form.get("signer_right"),
    ]

    student = Student.query.get(student_id)
    selected_signers = []
    for sid in signer_ids:
        signer = Signer.query.get(sid)
        if signer:
            selected_signers.append(signer.to_dict())

    if not student or len(selected_signers) != 3:
        return "Błąd: Nie znaleziono danych studenta lub sygnatariuszy.", 404

    try:
        context = student.to_dict()
        context["role_description"] = role_description
        context["achievements"] = achievements_list

        filename = generate_pdf(context, template_name, selected_signers)
        return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)
    except Exception as e:
        return str(e), 500
