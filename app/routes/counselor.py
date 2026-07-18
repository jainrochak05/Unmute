from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import extensions
from app.utils import utcnow

counselor_bp = Blueprint("counselor", __name__)


@counselor_bp.route("/", methods=["GET", "POST"])
@login_required
def counselor():
    if extensions.mongo_db is None:
        flash("Database connection unavailable.", "danger")
        return render_template("counselor.html")

    db = extensions.mongo_db
    col = db["counselor_requests"]

    if request.method == "POST":
        col.insert_one({
            "user_id": current_user.id,
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "preferred_date": request.form.get("preferred_date"),
            "preferred_time": request.form.get("preferred_time"),
            "message": request.form.get("message"),
            "created_at": utcnow(),
        })

        flash("Your appointment request has been submitted successfully.", "success")
        return redirect(url_for("counselor.counselor"))

    return render_template("counselor.html")
