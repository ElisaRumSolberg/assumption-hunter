class Address:
    def __init__(self, street: str, city: str):
        self.street = street
        self.city = city


class User:
    def __init__(self, name: str, email: str | None = None, address: "Address | None" = None):
        self.name = name
        self.email = email
        self.address = address


def format_billing_email(user: User) -> str:
    """Already guarded: falls back safely when email is missing.

    This is a TRAP for a naive detector — it looks like the same pattern as
    case_001 (`user.email.lower()`), but it is NOT an unverified assumption
    because the missing-email case is explicitly handled.
    """
    if not user.email:
        return f"{user.name} <no-email-on-file>"
    return f"{user.name} <{user.email.lower()}>"


def format_shipping_label(user: User) -> str:
    """Assumes every user has a complete shipping address — no guard, no fallback."""
    return f"{user.name}\n{user.address.street}, {user.address.city}"
