from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId

from app import extensions
from app.utils import utcnow

stories_bp = Blueprint("stories", __name__)

# -----------------------------
# Predefined Mood Tags
# -----------------------------

MOOD_TAGS = [
    "Peaceful",
    "Hopeful",
    "Happy",
    "Grateful",
    "Motivated",
    "Lonely",
    "Anxious",
    "Overwhelmed",
    "Heartbroken",
    "Confused",
    "Stressed",
    "Burnt Out"
]

REACTION_KEYS = {
    "relate",
    "hug",
    "thanks"
}


# ============================================================
# MY STORIES
# ============================================================

@stories_bp.route("/", methods=["GET", "POST"])
@login_required
def stories_home():

    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return render_template(
            "stories.html",
            stories=[],
            mood_tags=MOOD_TAGS
        )

    db = extensions.mongo_db
    stories_col = db["stories"]
    activities_col = db["activities"]

    # --------------------------------
    # Publish Story
    # --------------------------------

    if request.method == "POST":

        title = request.form.get("title", "").strip()

        content = request.form.get("content", "").strip()

        tags = request.form.getlist("tags")

        is_public = request.form.get("is_public") == "on"

        if not content:

            flash("Story cannot be empty.", "warning")

            return redirect(
                url_for("stories.stories_home")
            )

        story = {

            "user_id": current_user.id,

            "title": title if title else "Untitled Story",

            "content": content,

            "tags": tags,

            "is_public": is_public,

            "reactions": {

                "relate": 0,

                "hug": 0,

                "thanks": 0

            },

            "created_at": utcnow()

        }

        stories_col.insert_one(story)

        activities_col.insert_one({

            "user_id": current_user.id,

            "type": "story_shared",

            "created_at": utcnow(),

            "meta": {

                "title": story["title"]

            }

        })

        flash("Story published successfully.", "success")

        return redirect(
            url_for("stories.stories_home")
        )

    # --------------------------------
    # Only show current user's stories
    # --------------------------------

    my_stories = list(

        stories_col.find(

            {

                "user_id": current_user.id

            }

        ).sort(

            "created_at",

            -1

        )

    )

    return render_template(

        "stories.html",

        stories=my_stories,

        mood_tags=MOOD_TAGS

    )


# ============================================================
# COMMUNITY FEED
# ============================================================

@stories_bp.route("/feed")
@login_required
def community_feed():

    if extensions.mongo_db is None:

        flash("Database not connected.", "danger")

        return render_template(

            "feed.html",

            stories=[],

            mood_tags=MOOD_TAGS,

            selected_tag="",

            selected_sort="recent",

            search=""

        )

    db = extensions.mongo_db

    stories_col = db["stories"]

    search = request.args.get("search", "").strip()

    selected_tag = request.args.get("tag", "").strip()

    selected_sort = request.args.get("sort", "recent")

    query = {

        "is_public": True

    }

    if selected_tag:

        query["tags"] = selected_tag

    if search:

        query["content"] = {

            "$regex": search,

            "$options": "i"

        }
    from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from bson.objectid import ObjectId

from app import extensions
from app.utils import utcnow

stories_bp = Blueprint("stories", __name__)

# -----------------------------
# Predefined Mood Tags
# -----------------------------

MOOD_TAGS = [
    "Peaceful",
    "Hopeful",
    "Happy",
    "Grateful",
    "Motivated",
    "Lonely",
    "Anxious",
    "Overwhelmed",
    "Heartbroken",
    "Confused",
    "Stressed",
    "Burnt Out"
]

REACTION_KEYS = {
    "relate",
    "hug",
    "thanks"
}


# ============================================================
# MY STORIES
# ============================================================

@stories_bp.route("/", methods=["GET", "POST"])
@login_required
def stories_home():

    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return render_template(
            "stories.html",
            stories=[],
            mood_tags=MOOD_TAGS
        )

    db = extensions.mongo_db
    stories_col = db["stories"]
    activities_col = db["activities"]

    # --------------------------------
    # Publish Story
    # --------------------------------

    if request.method == "POST":

        title = request.form.get("title", "").strip()

        content = request.form.get("content", "").strip()

        tags = request.form.getlist("tags")

        is_public = request.form.get("is_public") == "on"

        if not content:

            flash("Story cannot be empty.", "warning")

            return redirect(
                url_for("stories.stories_home")
            )

        story = {

            "user_id": current_user.id,

            "title": title if title else "Untitled Story",

            "content": content,

            "tags": tags,

            "is_public": is_public,

            "reactions": {

                "relate": 0,

                "hug": 0,

                "thanks": 0

            },

            "created_at": utcnow()

        }

        stories_col.insert_one(story)

        activities_col.insert_one({

            "user_id": current_user.id,

            "type": "story_shared",

            "created_at": utcnow(),

            "meta": {

                "title": story["title"]

            }

        })

        flash("Story published successfully.", "success")

        return redirect(
            url_for("stories.stories_home")
        )

    # --------------------------------
    # Only show current user's stories
    # --------------------------------

    my_stories = list(

        stories_col.find(

            {

                "user_id": current_user.id

            }

        ).sort(

            "created_at",

            -1

        )

    )

    return render_template(

        "stories.html",

        stories=my_stories,

        mood_tags=MOOD_TAGS

    )


# ============================================================
# COMMUNITY FEED
# ============================================================

@stories_bp.route("/feed")
@login_required
def community_feed():

    if extensions.mongo_db is None:

        flash("Database not connected.", "danger")

        return render_template(

            "feed.html",

            stories=[],

            mood_tags=MOOD_TAGS,

            selected_tag="",

            selected_sort="recent",

            search=""

        )

    db = extensions.mongo_db

    stories_col = db["stories"]

    search = request.args.get("search", "").strip()

    selected_tag = request.args.get("tag", "").strip()

    selected_sort = request.args.get("sort", "recent")

    query = {

        "is_public": True

    }

    if selected_tag:

        query["tags"] = selected_tag

    if search:

        query["content"] = {

            "$regex": search,

            "$options": "i"

        }
    # --------------------------------
    # Sorting
    # --------------------------------

    if selected_sort == "oldest":

        stories = list(

            stories_col.find(query).sort(

                "created_at",

                1

            )

        )

    else:

        stories = list(

            stories_col.find(query).sort(

                "created_at",

                -1

            )

        )

    return render_template(

        "feed.html",

        stories=stories,

        mood_tags=MOOD_TAGS,

        selected_tag=selected_tag,

        selected_sort=selected_sort,

        search=search

    )


# ============================================================
# REACTIONS
# ============================================================

@stories_bp.route("/react/<story_id>/<reaction>", methods=["POST"])
@login_required
def react_story(story_id, reaction):

    if extensions.mongo_db is None:

        flash("Database not connected.", "danger")

        return redirect(

            url_for("stories.community_feed")

        )

    if reaction not in REACTION_KEYS:

        flash("Invalid reaction.", "warning")

        return redirect(

            url_for("stories.community_feed")

        )

    db = extensions.mongo_db

    stories_col = db["stories"]

    try:

        stories_col.update_one(

            {

                "_id": ObjectId(story_id),

                "is_public": True

            },

            {

                "$inc": {

                    f"reactions.{reaction}": 1

                }

            }

        )

    except Exception:

        flash("Unable to react to this story.", "warning")

    return redirect(

        url_for(

            "stories.community_feed",

            tag=request.args.get("tag", ""),

            sort=request.args.get("sort", "recent"),

            search=request.args.get("search", "")

        )

    )
