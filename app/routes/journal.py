from datetime import datetime, timezone, timedelta
from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, send_file
from flask_login import login_required, current_user
from bson.objectid import ObjectId
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app import extensions
from app.utils import utcnow
from app.services.activity_service import log_activity

journal_bp = Blueprint("journal", __name__)
UTC = timezone.utc


@journal_bp.route("/", methods=["GET", "POST"])
@login_required
def journal_home():
    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return render_template("journal.html", entries=[], q="", mood="", order="recent", date="")

    db = extensions.mongo_db
    col = db["journals"]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        mood_tag = request.form.get("mood_tag", "").strip().lower()

        if not content:
            flash("Journal content cannot be empty.", "warning")
            return redirect(url_for("journal.journal_home"))

        col.insert_one({
            "user_id": current_user.id,
            "title": title or "Untitled",
            "content": content,
            "mood_tag": mood_tag,
            "created_at": utcnow(),
        })

        log_activity(db, current_user.id, "journal_added", {"title": title or "Untitled"})
        flash("Journal saved.", "success")
        return redirect(url_for("journal.journal_home"))

    q = request.args.get("q", "").strip()
    mood = request.args.get("mood", "").strip().lower()
    order = request.args.get("order", "recent").strip().lower()
    date_str = request.args.get("date", "").strip()  # YYYY-MM-DD

    query = {"user_id": current_user.id}

    if q:
        query["$or"] = [
            {"title": {"$regex": q, "$options": "i"}},
            {"content": {"$regex": q, "$options": "i"}},
            {"mood_tag": {"$regex": q, "$options": "i"}},
        ]

    if mood:
        query["mood_tag"] = mood

    if date_str:
        try:
            day_start = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=UTC)
            day_end = day_start + timedelta(days=1)
            query["created_at"] = {"$gte": day_start, "$lt": day_end}
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "warning")

    sort_dir = -1 if order != "oldest" else 1
    entries = list(col.find(query).sort("created_at", sort_dir))

    return render_template(
        "journal.html",
        entries=entries,
        q=q,
        mood=mood,
        order=order,
        date=date_str
    )


@journal_bp.route("/delete/<entry_id>", methods=["POST"])
@login_required
def delete_entry(entry_id):
    if extensions.mongo_db is None:
        flash("Database not connected.", "danger")
        return redirect(url_for("journal.journal_home"))

    try:
        extensions.mongo_db["journals"].delete_one({"_id": ObjectId(entry_id), "user_id": current_user.id})
        flash("Entry deleted.", "info")
    except Exception:
        flash("Could not delete entry.", "danger")

    return redirect(url_for("journal.journal_home"))


@journal_bp.route("/export/txt")
@login_required
def export_txt():
    db = extensions.mongo_db
    if db is None:
        return Response("Database not connected.", mimetype="text/plain")

    entries = list(db["journals"].find({"user_id": current_user.id}).sort("created_at", -1))

    lines = []
    for e in entries:
        lines.append(f"Date: {e.get('created_at', '')}")
        lines.append(f"Mood: {e.get('mood_tag', '')}")
        lines.append(f"Title: {e.get('title', '')}")
        lines.append("Content:")
        lines.append(e.get("content", ""))
        lines.append("-" * 50)

    text = "\n".join(lines)
    return Response(
        text,
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment; filename=journals.txt"}
    )


@journal_bp.route("/export/pdf")
@login_required
def export_pdf():
    db = extensions.mongo_db
    if db is None:
        flash("Database not connected.", "danger")
        return redirect(url_for("journal.journal_home"))

    entries = list(db["journals"].find({"user_id": current_user.id}).sort("created_at", -1))

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 40

    p.setFont("Helvetica-Bold", 14)
    p.drawString(40, y, "Journal Export")
    y -= 24
    p.setFont("Helvetica", 10)

    for e in entries:
        block = [
            f"Date: {e.get('created_at', '')}",
            f"Mood: {e.get('mood_tag', '')}",
            f"Title: {e.get('title', '')}",
            "Content:",
            str(e.get("content", "")),
            "-" * 100
        ]
        for line in block:
            for chunk in [line[i:i+120] for i in range(0, len(line), 120)] or [""]:
                if y < 50:
                    p.showPage()
                    p.setFont("Helvetica", 10)
                    y = height - 40
                p.drawString(40, y, chunk)
                y -= 14

    p.save()
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="journals.pdf",
        mimetype="application/pdf"
    )
