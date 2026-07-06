from datetime import datetime, timedelta, timezone
from collections import Counter

UTC = timezone.utc


def to_aware_utc(dt):
    """
    Ensures every datetime is timezone-aware (UTC).
    Prevents comparisons between naive and aware datetimes.
    """
    if not isinstance(dt, datetime):
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)

    return dt.astimezone(UTC)


def _start_of_day(dt):
    dt = to_aware_utc(dt) or datetime.now(UTC)
    return datetime(dt.year, dt.month, dt.day, tzinfo=UTC)


def calculate_streak(moods):
    """
    Calculates consecutive daily mood logging streak.
    """

    if not moods:
        return 0

    logged_days = set()

    for mood in moods:
        created = to_aware_utc(mood.get("created_at"))

        if created:
            logged_days.add(
                (
                    created.year,
                    created.month,
                    created.day,
                )
            )

    streak = 0
    cursor = _start_of_day(datetime.now(UTC))

    while (
        cursor.year,
        cursor.month,
        cursor.day,
    ) in logged_days:

        streak += 1
        cursor -= timedelta(days=1)

    return streak


def dashboard_stats(db, user_id):

    moods_col = db["moods"]
    journals_col = db["journals"]
    stories_col = db["stories"]
    chats_col = db["ai_conversations"]
    prompts_col = db["prompt_responses"]

    moods = list(
        moods_col
        .find({"user_id": user_id})
        .sort("created_at", -1)
        .limit(200)
    )

    current_mood = moods[0]["mood_score"] if moods else None
    streak = calculate_streak(moods)

    total_journals = journals_col.count_documents(
        {"user_id": user_id}
    )

    total_stories = stories_col.count_documents(
        {"user_id": user_id}
    )

    total_ai_chats = chats_col.count_documents(
        {"user_id": user_id}
    )

    today = _start_of_day(datetime.now(UTC))
    tomorrow = today + timedelta(days=1)

    prompt_done = (
        prompts_col.count_documents(
            {
                "user_id": user_id,
                "created_at": {
                    "$gte": today,
                    "$lt": tomorrow,
                },
            }
        )
        > 0
    )

    return {
        "current_mood": current_mood,
        "mood_streak": streak,
        "total_journals": total_journals,
        "total_stories": total_stories,
        "total_ai_chats": total_ai_chats,
        "prompt_done": prompt_done,
    }
def mood_trends(db, user_id):
    moods = list(
        db["moods"]
        .find({"user_id": user_id})
        .sort("created_at", 1)
    )

    now = datetime.now(UTC)

    normalized = []

    for mood in moods:
        created = to_aware_utc(mood.get("created_at"))
        score = mood.get("mood_score")

        if created is not None and isinstance(score, (int, float)):
            normalized.append({
                "created_at": created,
                "mood_score": score,
            })

    # ---------- Weekly ----------

    weekly_labels = []
    weekly_values = []

    for i in range(6, -1, -1):

        day_start = _start_of_day(now - timedelta(days=i))
        day_end = day_start + timedelta(days=1)

        scores = [
            x["mood_score"]
            for x in normalized
            if day_start <= x["created_at"] < day_end
        ]

        weekly_labels.append(day_start.strftime("%a"))
        weekly_values.append(
            round(sum(scores) / len(scores), 2)
            if scores else None
        )

    # ---------- Monthly ----------

    monthly_labels = []
    monthly_values = []

    for i in range(29, -1, -1):

        day_start = _start_of_day(now - timedelta(days=i))
        day_end = day_start + timedelta(days=1)

        scores = [
            x["mood_score"]
            for x in normalized
            if day_start <= x["created_at"] < day_end
        ]

        monthly_labels.append(day_start.strftime("%d %b"))
        monthly_values.append(
            round(sum(scores) / len(scores), 2)
            if scores else None
        )

    all_scores = [x["mood_score"] for x in normalized]

    stats = {
        "avg_mood": round(sum(all_scores) / len(all_scores), 2)
        if all_scores else 0,
        "highest_mood": max(all_scores)
        if all_scores else 0,
        "lowest_mood": min(all_scores)
        if all_scores else 0,
        "total_entries": len(all_scores),
    }

    return {
        "weekly": {
            "labels": weekly_labels,
            "values": weekly_values,
        },
        "monthly": {
            "labels": monthly_labels,
            "values": monthly_values,
        },
        "stats": stats,
    }


def emotional_insights(db, user_id):

    moods = list(db["moods"].find({"user_id": user_id}))
    journals = list(db["journals"].find({"user_id": user_id}))

    normalized = []

    for mood in moods:
        created = to_aware_utc(mood.get("created_at"))
        score = mood.get("mood_score")

        if created is not None and isinstance(score, (int, float)):
            normalized.append({
                "created_at": created,
                "mood_score": score,
            })

    if not normalized:
        return {
            "most_common_emotion": "N/A",
            "best_week_avg": 0,
            "lowest_week_avg": 0,
            "most_active_journaling_day": "N/A",
            "avg_weekly_mood": 0,
        }

    def emotion(score):
        if score >= 9:
            return "Peaceful"
        if score >= 7:
            return "Hopeful"
        if score >= 4:
            return "Anxious"
        return "Heavy"

    emotion_counts = Counter(
        emotion(m["mood_score"])
        for m in normalized
    )

    most_common_emotion = emotion_counts.most_common(1)[0][0]

    # ---------- Weekly averages ----------

    week_map = {}

    for mood in normalized:

        d = mood["created_at"]

        key = (
            f"{d.isocalendar().year}"
            f"-W{d.isocalendar().week}"
        )

        week_map.setdefault(key, []).append(
            mood["mood_score"]
        )

    weekly_avgs = (
        [sum(v) / len(v) for v in week_map.values()]
        if week_map else [0]
    )

    # ---------- Journaling ----------

    day_counts = Counter()

    for journal in journals:

        created = to_aware_utc(
            journal.get("created_at")
        )

        if created:
            day_counts[
                created.strftime("%A")
            ] += 1

    return {
        "most_common_emotion": most_common_emotion,
        "best_week_avg": round(max(weekly_avgs), 2),
        "lowest_week_avg": round(min(weekly_avgs), 2),
        "most_active_journaling_day":
            day_counts.most_common(1)[0][0]
            if day_counts else "N/A",
        "avg_weekly_mood":
            round(
                sum(weekly_avgs) / len(weekly_avgs),
                2,
            ),
    }
