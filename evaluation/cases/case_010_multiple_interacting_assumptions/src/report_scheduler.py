import os
from datetime import datetime, timezone


def schedule_report(run_at: datetime) -> str:
    """Makes two independent hidden assumptions:
    1. REPORT_TIMEZONE is always set in the environment.
    2. run_at is always a timezone-aware datetime, comparable to utcnow().
    """
    tz_name = os.environ["REPORT_TIMEZONE"]
    now = datetime.now(timezone.utc)
    if run_at < now:
        raise ValueError("Cannot schedule a report in the past")
    return f"Report scheduled at {run_at.isoformat()} ({tz_name})"
