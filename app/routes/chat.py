from flask import Blueprint, render_template, request, current_app
from flask_login import login_required, current_user
from app import extensions
from app.utils import utcnow
from app.services.gemini_service import get_chat_reply
from app.services.activity_service import log_activity

chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["GET", "POST"])
@login_required
def chat_home():
    reply, error, user_message = None, None, ""
    active_model = current_app.config.get("GEMINI_MODEL")

    if request.method == "POST":
        user_message = request.form.get("message", "").strip()
        if user_message:
            reply, error = get_chat_reply(
                current_app.config.get("GEMINI_API_KEY"),
                active_model,
                user_message
            )

            if extensions.mongo_db is not None:
                extensions.mongo_db["ai_conversations"].insert_one({
                    "user_id": current_user.id,
                    "message": user_message,
                    "reply": reply,
                    "error": error,
                    "created_at": utcnow(),
                })
                log_activity(extensions.mongo_db, current_user.id, "ai_conversation_started", {"ok": error is None})

    return render_template("chat.html", reply=reply, error=error, user_message=user_message, active_model=active_model)
