# case_002 — Empty Search Results

`src/search.py`'s `best_match` assumes `search_products` always returns at
least one result and indexes `results[0]` directly.

## Expected agent finding

- **Assumption:** search results are never empty.
- **Evidence:** `src/search.py` (`best_match`).
- **Counterexample:** query with no matches in the catalog.
- **Expected failure:** `IndexError: list index out of range`.
