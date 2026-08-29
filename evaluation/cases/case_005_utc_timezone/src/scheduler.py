from datetime import datetime, timezone


def is_event_upcoming(event_time: datetime) -> bool:
    """Assumes event_time is always a timezone-aware UTC datetime."""
    now = datetime.now(timezone.utc)
    return event_time > now
