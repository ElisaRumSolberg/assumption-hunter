import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.settings_loader import load_settings


def test_load_settings_raises_when_file_missing(tmp_path):
    missing_path = tmp_path / "does_not_exist.json"
    with pytest.raises(FileNotFoundError):
        load_settings(str(missing_path))
