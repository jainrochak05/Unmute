from datetime import datetime, timedelta, timezone
from collections import Counter

UTC = timezone.utc


def to_aware_utc(dt):
    if not isinstance(dt, datetime):
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def start_of_day(dt):
    d = to_aware_utc(dt) or datetime.now(UTC)
    return datetime(d.year, d.month, d.day, tzinfo=UTC)


def calculate_streak(moods):
    if not moods:
        return 0

    days = set()
    for m in moods:
        d = to_aware_utc(m.get("created_at"))
        if d:
            days.add((d.year, d.month, d.day))

    streak = 0
    cursor = start_of_day(datetime.now(UTC))
    while (cursor.year, cursor.month, cursor.day) in days:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def dashboard_stats(db, user_id):
    moods = list(db["moods"].find({"user_id": user_id}).sort("created_at", -1).limit(200))

    current_mood = moods[0].get("mood_score") if moods else None
    streak = calculate_streak(moods)

    total_journals = db["journals"].count_documents({"user_id": user_id})
    total_stories = db["stories"].count_documents({"user_id": user_id})
    total_ai_chats = db["ai_conversations"].count_documents({"user_id": user_id})

    today = start_of_day(datetime.now(UTC))
    tomorrow = today + timedelta(days=1)
    prompt_done = db["prompt_responses"].count_documents({
        "user_id": user_id,
        "created_at": {"$gte": today, "$lt": tomorrow}
    }) > 0

    return {
        "current_mood": current_mood,
        "mood_streak": streak,
        "total_journals": total_journals,
        "total_stories": total_stories,
        "total_ai_chats": total_ai_chats,
        "prompt_done": prompt_done,
    }


def mood_trends(db, user_id):
    moods = list(db["moods"].find({"user_id": user_id}).sort("created_at", 1))
    now = datetime.now(UTC)

    normalized = []
    for m in moods:
        d = to_aware_utc(m.get("created_at"))
        score = m.get("mood_score")
        if d is not None and isinstance(score, (int, float)):
            normalized.append({"created_at": d, "mood_score": score})

    weekly_labels, weekly_values = [], []
    for i in range(6, -1, -1):
        day_start = start_of_day(now - timedelta(days=i))
        day_end = day_start + timedelta(days=1)
        scores = [x["mood_score"] for x in normalized if day_start <= x["created_at"] < day_end]
        weekly_labels.append(day_start.strftime("%a"))
        weekly_values.append(round(sum(scores)/len(scores), 2) if scores else None)

    monthly_labels, monthly_values = [], []
    for i in range(29, -1, -1):
        day_start = start_of_day(now - timedelta(days=i))
        day_end = day_start + timedelta(days=1)
        scores = [x["mood_score"] for x in normalized if day_start <= x["created_at"] < day_end]
        monthly_labels.append(day_start.strftime("%d %b"))
        monthly_values.append(round(sum(scores)/len(scores), 2) if scores else None)

    all_scores = [x["mood_score"] for x in normalized]
    stats = {
        "avg_mood": round(sum(all_scores)/len(all_scores), 2) if all_scores else 0,
        "highest_mood": max(all_scores) if all_scores else 0,
        "lowest_mood": min(all_scores) if all_scores else 0,
        "total_entries": len(all_scores),
    }

    return {
        "weekly": {"labels": weekly_labels, "values": weekly_values},
        "monthly": {"labels": monthly_labels, "values": monthly_values},
        "stats": stats,
    }


def emotional_insights(db, user_id):
    moods = list(db["moods"].find({"user_id": user_id}))
    journals = list(db["journals"].find({"user_id": user_id}))

    valid = []
    for m in moods:
        d = to_aware_utc(m.get("created_at"))
        score = m.get("mood_score")
        if d is not None and isinstance(score, (int, float)):
            valid.append({"created_at": d, "mood_score": score})

    if not valid:
        return {
            "most_common_emotion": "N/A",
            "best_week_avg": 0,
            "lowest_week_avg": 0,
            "most_active_journaling_day": "N/A",
            "avg_weekly_mood": 0,
        }

    def emotion(s):
        if s >= 9: return "Excellent"
        if s >= 7: return "Happy"
        if s >= 5: return "Neutral"
        if s >= 3: return "Sad"
        return "Very Low"

    most_common_emotion = Counter(emotion(x["mood_score"]) for x in valid).most_common(1)[0][0]

    week_map = {}
    for x in valid:
        d = x["created_at"]
        key = f"{d.isocalendar().year}-W{d.isocalendar().week}"
        week_map.setdefault(key, []).append(x["mood_score"])

    week_avgs = [sum(v)/len(v) for v in week_map.values()] if week_map else [0]

    day_counts = Counter()
    for j in journals:
        d = to_aware_utc(j.get("created_at"))
        if d:
            day_counts[d.strftime("%A")] += 1

    return {
        "most_common_emotion": most_common_emotion,
        "best_week_avg": round(max(week_avgs), 2),
        "lowest_week_avg": round(min(week_avgs), 2),
        "most_active_journaling_day": day_counts.most_common(1)[0][0] if day_counts else "N/A",
        "avg_weekly_mood": round(sum(week_avgs)/len(week_avgs), 2),
    }
