from typing import Callable


def fetch_weather(http_get: Callable[[str], object], city: str) -> dict:
    """Assumes the external weather API always returns a valid JSON body."""
    response = http_get(f"https://api.example.com/weather?city={city}")
    return response.json()
