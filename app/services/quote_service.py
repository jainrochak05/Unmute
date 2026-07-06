from datetime import datetime, timezone

QUOTES = [
    "Small steps are still progress.",
    "You are allowed to grow at your own pace.",
    "Your feelings are valid, and they matter.",
    "Today is a new chance to be kind to yourself.",
    "Healing is not linear, and that is okay.",
    "You have survived 100% of your hardest days.",
    "Pause. Breathe. Begin again.",
]


def get_daily_quote():
    day_index = datetime.now(timezone.utc).toordinal()
    return QUOTES[day_index % len(QUOTES)]
