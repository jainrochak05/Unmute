from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 6:
            flash("Please provide valid details. Password must be at least 6 characters.", "danger")
            return render_template("register.html")
        user = User.create(name, email, password)
        if not user:
            flash("Email already exists.", "warning")
            return render_template("register.html")
        login_user(user)
        flash("Welcome to Unmute!", "success")
        return redirect(url_for("home.index"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = User.get_by_email(email)
        if not user or not user.verify_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("login.html")
        login_user(user)
        flash("Logged in successfully.", "success")
        return redirect(url_for("home.index"))
    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
