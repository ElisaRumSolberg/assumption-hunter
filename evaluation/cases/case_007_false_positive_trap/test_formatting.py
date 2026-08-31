import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.formatting import User, format_billing_email, format_shipping_label


def test_format_billing_email_handles_missing_email_safely():
    user = User(name="Ali", email=None)
    assert format_billing_email(user) == "Ali <no-email-on-file>"


def test_format_shipping_label_raises_on_missing_address():
    user = User(name="Ali", email="ali@example.com", address=None)
    with pytest.raises(AttributeError):
        format_shipping_label(user)
