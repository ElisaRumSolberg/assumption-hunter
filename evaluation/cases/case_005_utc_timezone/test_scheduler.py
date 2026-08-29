import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.scheduler import is_event_upcoming


def test_is_event_upcoming_raises_on_naive_datetime():
    naive_local_time = datetime(2030, 1, 1, 12, 0, 0)
    with pytest.raises(TypeError):
        is_event_upcoming(naive_local_time)
