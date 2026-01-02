import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.database import db_session
from app.models import User, Student, Signer

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@admin_bp.route("/users", methods=["GET", "POST"])
@login_required
def manage_users():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            flash("Użytkownik już istnieje", "warning")
        else:
            new_user = User(username=username)
            new_user.set_password(password)
            db_session.add(new_user)
            db_session.commit()
            flash("Dodano użytkownika", "success")

    users = User.query.all()
    return render_template("admin/manage_users.html", users=users)


@admin_bp.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("Nie możesz usunąć samego siebie!", "danger")
        return redirect(url_for("admin.manage_users"))

    user = User.query.get(user_id)
    if user:
        db_session.delete(user)
        db_session.commit()
        flash("Usunięto użytkownika", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/signers", methods=["GET", "POST"])
@login_required
def manage_signers():
    if request.method == "POST":
        signer_id = request.form.get("signer_id")
        name = request.form.get("name")
        role = request.form.get("role")

        if signer_id:
            signer = Signer.query.get(signer_id)
            if signer:
                signer.name = name
                signer.role = role
        else:
            signer = Signer(name=name, role=role)
            db_session.add(signer)

        db_session.commit()
        flash("Zapisano dane sygnatariusza", "success")

    signers = Signer.query.all()
    return render_template("admin/manage_signers.html", signers=signers)


@admin_bp.route("/delete_signer/<int:id>")
@login_required
def delete_signer(id):
    item = Signer.query.get(id)
    if item:
        db_session.delete(item)
        db_session.commit()
    return redirect(url_for("admin.manage_signers"))


@admin_bp.route("/students", methods=["GET", "POST"])
@login_required
def manage_students():
    faculties = [
        ("W1", "Wydział Mechaniczny"),
        ("W2", "Wydział Elektrotechniki, Elektroniki, Informatyki i Automatyki"),
        ("W3", "Wydział Chemiczny"),
        ("W4", "Wydział Technologii Materiałów i Wzornictwa Tekstyliów"),
        ("W5", "Wydział Biotechnologii i Nauk o Żywności"),
        ("W6", "Wydział Budownictwa, Architektury i Inżynierii Środowiska"),
        ("W7", "Wydział Fizyki Technicznej, Informatyki i Matematyki Stosowanej"),
        ("W8", "Wydział Organizacji i Zarządzania"),
        ("W9", "Wydział Inżynierii Procesowej i Ochrony Środowiska"),
        ("IFE", "Centrum Kształcenia Międzynarodowego (IFE)"),
    ]

    departments = [
        "Programista",
        "Mechanik",
        "Kierowca",
        "Marketing",
        "Elektronik",
        "Team Manager",
    ]

    if request.method == "POST":
        logger.info(
            f"Received POST request to add/edit student. Form data: {request.form}"
        )

        try:
            student_id = request.form.get("student_id")

            if student_id:
                student = Student.query.get(student_id)
                logger.info(f"Editing existing student ID: {student_id}")
            else:
                student = Student()
                logger.info("Creating new student entry.")

            student.name = request.form.get("name")
            student.index = request.form.get("index")
            student.major = request.form.get("major")
            student.gender = request.form.get("gender")
            student.faculty = request.form.get("faculty")
            student.department = request.form.get("department")

            if not student.name or not student.index:
                logger.warning(
                    f"Validation failed: Name='{student.name}', Index='{student.index}'"
                )
                flash("Imię i Indeks są wymagane.", "danger")
            else:
                if not student_id:
                    db_session.add(student)

                db_session.commit()
                logger.info(f"Successfully saved student: {student.name}")
                flash("Zapisano dane studenta", "success")

        except Exception as e:
            db_session.rollback()
            logger.error("Error occurred while saving student", exc_info=True)
            flash(f"Błąd systemowy: {str(e)}", "danger")

    students = Student.query.all()
    return render_template(
        "admin/manage_students.html",
        students=students,
        faculties=faculties,
        departments=departments,
    )


@admin_bp.route("/delete_student/<int:id>")
@login_required
def delete_student(id):
    item = Student.query.get(id)
    if item:
        db_session.delete(item)
        db_session.commit()
    return redirect(url_for("admin.manage_students"))
