import os


def get_database_url() -> str:
    """Assumes DATABASE_URL is always set in the environment."""
    return os.environ["DATABASE_URL"]


def build_connection_info() -> dict:
    return {"url": get_database_url(), "pool_size": 5}
