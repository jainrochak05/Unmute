from flask import Blueprint, render_template
from flask_login import login_required
from datetime import datetime

prompts_bp = Blueprint("prompts", __name__)

PROMPTS = [
    "What emotion did you feel most strongly today, and why?",
    "What is one small thing that gave you peace today?",
    "What negative thought can you gently challenge right now?",
    "What would you tell a friend feeling exactly like you do?",
    "List three things you can control this week."
]


@prompts_bp.route("/")
@login_required
def prompt_home():
    idx = datetime.utcnow().timetuple().tm_yday % len(PROMPTS)
    return render_template("prompts.html", prompt=PROMPTS[idx])
