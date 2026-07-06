from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app import extensions
from app.services.analytics_service import dashboard_stats, mood_trends, emotional_insights
from app.services.quote_service import get_daily_quote
from app.services.mood_mapper import mood_meta

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
@login_required
def dashboard_home():
    if extensions.mongo_db is None:
        return render_template("dashboard.html", stats={}, trends={}, insights={}, quote="")

    db = extensions.mongo_db
    stats = dashboard_stats(db, current_user.id)
    trends = mood_trends(db, current_user.id)
    insights = emotional_insights(db, current_user.id)

    current_mood = stats.get("current_mood")
    emoji, label, color = mood_meta(current_mood) if current_mood else ("—", "Not logged", "#94a3b8")

    # reminder: mood not logged today
    reminder = None
    if current_mood is None or stats.get("mood_streak", 0) == 0:
        reminder = "You haven’t logged today’s mood yet. Take a minute to check in with yourself."

    recent_activities = list(
        db["activities"].find({"user_id": current_user.id}).sort("created_at", -1).limit(8)
    )

    return render_template(
        "dashboard.html",
        stats=stats,
        trends=trends,
        insights=insights,
        quote=get_daily_quote(),
        current_mood_emoji=emoji,
        current_mood_label=label,
        current_mood_color=color,
        reminder=reminder,
        recent_activities=recent_activities
    )
