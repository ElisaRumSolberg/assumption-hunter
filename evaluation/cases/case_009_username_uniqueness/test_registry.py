import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.registry import UserRegistry


def test_register_silently_overwrites_duplicate_username():
    """Demonstrates the bug: registering a second account under an existing
    username silently overwrites the first, with no conflict error raised."""
    registry = UserRegistry()
    registry.register("alice", "alice@old-example.com")

    registry.register("alice", "attacker@example.com")

    assert registry._users["alice"] == "attacker@example.com"
