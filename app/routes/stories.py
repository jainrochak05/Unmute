from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from app import extensions
from app.utils import utcnow

stories_bp = Blueprint("stories", __name__)

REACTION_KEYS = {"love", "hug", "stay_strong", "appreciate"}


def _parse_tags(raw: str):
    # input: "lonely, left out, anxious"
    return [t.strip().lower() for t in raw.split(",") if t.strip()]


@stories_bp.route("/", methods=["GET", "POST"])
@login_required
def stories_home():
    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return render_template("stories.html", stories=[], all_tags=[], selected_tag="")

    col = extensions.mongo_db["stories"]
    activities = extensions.mongo_db["activities"]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        tags_raw = request.form.get("tags", "").strip()
        is_public = request.form.get("is_public") == "on"

        if not content:
            flash("Story cannot be empty.", "warning")
            return redirect(url_for("stories.stories_home"))

        tags = _parse_tags(tags_raw)

        col.insert_one({
            "user_id": current_user.id,
            "title": title or "Untitled Story",
            "content": content,
            "tags": tags,
            "is_public": True if is_public else False,
            "reactions": {"love": 0, "hug": 0, "stay_strong": 0, "appreciate": 0},
            "created_at": utcnow(),
        })

        activities.insert_one({
            "user_id": current_user.id,
            "type": "story_shared",
            "meta": {"title": title or "Untitled Story"},
            "created_at": utcnow(),
        })

        flash("Story shared successfully.", "success")
        return redirect(url_for("stories.stories_home"))

    selected_tag = request.args.get("tag", "").strip().lower()
    query = {"is_public": True}
    if selected_tag:
        query["tags"] = selected_tag

    stories = list(col.find(query).sort("created_at", -1).limit(100))
    all_tags = sorted(
        {tag for s in col.find({"is_public": True}, {"tags": 1}) for tag in s.get("tags", [])}
    )

    return render_template(
        "stories.html",
        stories=stories,
        all_tags=all_tags,
        selected_tag=selected_tag,
    )


@stories_bp.route("/react/<story_id>/<reaction>", methods=["POST"])
@login_required
def react_story(story_id, reaction):
    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return redirect(url_for("stories.stories_home"))

    if reaction not in REACTION_KEYS:
        flash("Invalid reaction.", "warning")
        return redirect(url_for("stories.stories_home"))

    col = extensions.mongo_db["stories"]
    col.update_one(
        {"_id": ObjectId(story_id), "is_public": True},
        {"$inc": {f"reactions.{reaction}": 1}}
    )

    return redirect(url_for("stories.stories_home", tag=request.args.get("tag", "")))
