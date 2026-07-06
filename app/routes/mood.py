from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import extensions
from app.utils import utcnow, parse_int
from app.services.activity_service import log_activity
from app.services.gemini_service import get_chat_reply

mood_bp = Blueprint("mood", __name__)

@mood_bp.route("/", methods=["GET", "POST"])
@login_required
def mood_home():
    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return render_template("mood.html", history=[], ai_reflection=None)

    db = extensions.mongo_db
    col = db["moods"]
    ai_reflection = None

    if request.method == "POST":
        mood_score = parse_int(request.form.get("mood_score"), 0)
        note = request.form.get("note", "").strip()

        if mood_score < 1 or mood_score > 10:
            flash("Mood score must be between 1 and 10.", "warning")
            return redirect(url_for("mood.mood_home"))

        col.insert_one({
            "user_id": current_user.id,
            "mood_score": mood_score,
            "note": note,
            "created_at": utcnow(),
        })

        log_activity(db, current_user.id, "mood_logged", {"score": mood_score})

        # AI Mood Reflection (short)
        prompt = (
            f"User logged mood {mood_score}/10 with note: '{note}'. "
            "Give a concise supportive reflection: acknowledge mood, one encouraging line, "
            "one practical wellness action, and one optional reflective question. "
            "Do not diagnose."
        )
        reply, err = get_chat_reply(
            current_app.config.get("GEMINI_API_KEY"),
            current_app.config.get("GEMINI_MODEL"),
            prompt
        )
        ai_reflection = reply if reply else "Thanks for checking in. Take one slow deep breath and be gentle with yourself."

        flash("Mood logged.", "success")
        history = list(col.find({"user_id": current_user.id}).sort("created_at", -1).limit(20))
        return render_template("mood.html", history=history, ai_reflection=ai_reflection)

    history = list(col.find({"user_id": current_user.id}).sort("created_at", -1).limit(20))
    return render_template("mood.html", history=history, ai_reflection=ai_reflection)
