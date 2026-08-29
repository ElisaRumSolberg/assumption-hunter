import json


def load_settings(config_path: str) -> dict:
    """Assumes the config file always exists at the given path."""
    with open(config_path) as f:
        return json.load(f)
