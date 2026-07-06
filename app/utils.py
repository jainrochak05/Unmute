from datetime import datetime, timezone


def utcnow():
    return datetime.now(timezone.utc)


def parse_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default
