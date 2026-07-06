from flask import Blueprint, render_template
from flask_login import current_user

from app.services.quote_service import get_daily_quote

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def index():

    return render_template(
        "index.html",
        user=current_user if current_user.is_authenticated else None,
        quote=get_daily_quote()
    )
