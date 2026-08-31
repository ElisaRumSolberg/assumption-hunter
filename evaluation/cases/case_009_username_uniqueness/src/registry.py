class UserRegistry:
    def __init__(self):
        self._users: dict[str, str] = {}

    def register(self, username: str, email: str) -> str:
        """Assumes usernames are always unique — silently overwrites any
        existing account with the same username instead of rejecting the
        registration or raising a conflict error."""
        self._users[username] = email
        return self._users[username]
