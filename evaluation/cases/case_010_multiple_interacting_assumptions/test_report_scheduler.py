import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.report_scheduler import schedule_report


def test_schedule_report_raises_when_timezone_env_var_missing(monkeypatch):
    monkeypatch.delenv("REPORT_TIMEZONE", raising=False)
    future_time = datetime.now(timezone.utc) + timedelta(days=1)
    with pytest.raises(KeyError):
        schedule_report(future_time)


def test_schedule_report_raises_on_naive_datetime(monkeypatch):
    monkeypatch.setenv("REPORT_TIMEZONE", "UTC")
    naive_future_time = datetime.now() + timedelta(days=1)
    with pytest.raises(TypeError):
        schedule_report(naive_future_time)
