import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.users import User, normalize_email


def test_normalize_email_raises_on_missing_email():
    user = User(name="Ali", email=None)
    with pytest.raises(AttributeError):
        normalize_email(user)
