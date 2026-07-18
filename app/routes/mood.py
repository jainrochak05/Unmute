from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import extensions
from app.utils import utcnow, parse_int
from app.services.activity_service import log_activity
from app.services.gemini_service import get_chat_reply

mood_bp = Blueprint("mood", __name__)

MOODS = {
    9: "Peaceful",
    7: "Hopeful",
    4: "Anxious",
    2: "Heavy",
}


@mood_bp.route("/", methods=["GET", "POST"])
@login_required
def mood_home():
    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return render_template(
            "mood.html",
            history=[],
            ai_reflection=None,
            show_counselor_alert=False,
        )

    db = extensions.mongo_db
    col = db["moods"]

    ai_reflection = None

    if request.method == "POST":

        mood_score = parse_int(request.form.get("mood_score"), 0)

        if mood_score not in MOODS:
            flash("Please select a mood.", "warning")
            return redirect(url_for("mood.mood_home"))

        col.insert_one({
            "user_id": current_user.id,
            "mood_score": mood_score,
            "created_at": utcnow(),
        })

        log_activity(
            db,
            current_user.id,
            "mood_logged",
            {"score": mood_score},
        )

        prompt = f"""
The user selected the mood "{MOODS[mood_score]}".

Write a supportive wellbeing reflection followed by a motivational quote.

Maximum 50 words.

Structure:

🌿 Acknowledge the feeling.

💛 Give one encouraging perspective.

✨ Suggest one simple action for today.

Do not ask follow-up questions.

Do not diagnose.

Keep it warm, reassuring and easy to understand.
"""

        reply, err = get_chat_reply(
            current_app.config.get("GEMINI_API_KEY"),
            current_app.config.get("GEMINI_MODEL"),
            prompt,
        )

        ai_reflection = (
            reply
            if reply
            else "Thank you for checking in today. Every emotion deserves space, and taking a moment to notice how you feel is already a positive step."
        )

        flash("Mood logged successfully!", "success")

    history = list(
        col.find({"user_id": current_user.id})
        .sort("created_at", -1)
        .limit(20)
    )

    # ---------- Counselor Recommendation ----------
    show_counselor_alert = False

    recent_moods = history[:5]

    if len(recent_moods) == 5:
        avg_score = sum(m["mood_score"] for m in recent_moods) / 5

        # Recommend counselor if average mood is Anxious/Heavy
        if avg_score <= 4:
            show_counselor_alert = True

    return render_template(
        "mood.html",
        history=history,
        ai_reflection=ai_reflection,
        show_counselor_alert=show_counselor_alert,
    )
