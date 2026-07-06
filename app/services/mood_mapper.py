def mood_meta(score: int):
    """
    Returns (emoji, label, color) for mood score 1-10
    """
    try:
        s = int(score)
    except Exception:
        s = 0

    if s >= 9:
        return "😊", "Excellent", "#22c55e"
    if s >= 7:
        return "🙂", "Happy", "#84cc16"
    if s >= 5:
        return "😐", "Neutral", "#eab308"
    if s >= 3:
        return "😔", "Sad", "#f97316"
    return "😢", "Very Low", "#ef4444"
