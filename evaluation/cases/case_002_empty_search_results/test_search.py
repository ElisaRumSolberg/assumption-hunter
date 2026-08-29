import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.search import best_match


def test_best_match_raises_on_no_results():
    catalog = [{"name": "Blue Shirt"}, {"name": "Red Shoes"}]
    with pytest.raises(IndexError):
        best_match(catalog, "nonexistent-product")
