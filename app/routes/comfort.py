from flask import Blueprint, render_template
from flask_login import login_required

comfort_bp = Blueprint("comfort", __name__)


@comfort_bp.route("/")
@login_required
def comfort_home():
    return render_template("comfort.html")
