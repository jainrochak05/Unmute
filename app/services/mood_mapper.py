def mood_meta(score):
    """
    Maps the stored mood score to the mood displayed in the UI.
    Returns:
        (emoji, label, color)
    """

    mapping = {
        9: ("🌿", "Peaceful", "#22c55e"),
        7: ("☀️", "Hopeful", "#84cc16"),
        4: ("🌧️", "Anxious", "#f59e0b"),
        2: ("🌑", "Heavy", "#ef4444"),
    }

    try:
        score = int(score)
    except (TypeError, ValueError):
        score = 2

    return mapping.get(score, ("❓", "Unknown", "#94a3b8"))
