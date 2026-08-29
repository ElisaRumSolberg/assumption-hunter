class User:
    def __init__(self, name: str, email: str | None = None):
        self.name = name
        self.email = email


def normalize_email(user: User) -> str:
    """Assumes every user has a non-null email address."""
    return user.email.lower().strip()


def build_display_name(user: User) -> str:
    return f"{user.name} <{normalize_email(user)}>"
