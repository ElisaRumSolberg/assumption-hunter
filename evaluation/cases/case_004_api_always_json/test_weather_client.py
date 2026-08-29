import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.weather_client import fetch_weather


class FakeNonJsonResponse:
    def __init__(self, text: str):
        self.text = text

    def json(self):
        raise ValueError("Expecting value: line 1 column 1 (char 0)")


def test_fetch_weather_raises_when_api_returns_non_json():
    def fake_get(_url):
        return FakeNonJsonResponse("<html>503 Service Unavailable</html>")

    with pytest.raises(ValueError):
        fetch_weather(fake_get, "Oslo")
