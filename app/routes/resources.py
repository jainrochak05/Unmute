from flask import Blueprint, render_template
from flask_login import login_required

resources_bp = Blueprint("resources", __name__)

RESOURCES = [
    {"title": "988 Suicide & Crisis Lifeline (US)", "link": "https://988lifeline.org/"},
    {"title": "NAMI Mental Health Resources", "link": "https://www.nami.org/help"},
    {"title": "Mindfulness Breathing Exercise", "link": "https://www.mindful.org/breathing-meditation/"},
]

@resources_bp.route("/")
@login_required
def resources_home():
    return render_template("resources.html", resources=RESOURCES)
