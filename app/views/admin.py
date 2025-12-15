from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.database import db_session
from app.models import User, Student, Signer

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


# --- USERS ---
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


# --- SIGNERS ---
@admin_bp.route("/signers", methods=["GET", "POST"])
@login_required
def manage_signers():
    if request.method == "POST":
        name = request.form.get("name")
        role = request.form.get("role")

        signer = Signer(name=name, role=role)
        db_session.add(signer)
        db_session.commit()
        flash("Dodano sygnatariusza", "success")

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


# --- STUDENTS ---
@admin_bp.route("/students", methods=["GET", "POST"])
@login_required
def manage_students():
    if request.method == "POST":
        try:
            student = Student(
                name=request.form["name"],
                index=request.form["index"],
                major=request.form["major"],
                gender=request.form["gender"],
                semester=request.form["semester"],
                year=request.form["year"],
                department=request.form["department"],
            )
            db_session.add(student)
            db_session.commit()
            flash("Dodano studenta", "success")
        except Exception as e:
            flash(f"Błąd: {e}", "danger")

    students = Student.query.all()
    return render_template("admin/manage_students.html", students=students)


@admin_bp.route("/delete_student/<int:id>")
@login_required
def delete_student(id):
    item = Student.query.get(id)
    if item:
        db_session.delete(item)
        db_session.commit()
    return redirect(url_for("admin.manage_students"))
