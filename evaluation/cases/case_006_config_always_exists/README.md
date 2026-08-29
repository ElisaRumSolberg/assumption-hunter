# case_006 — Config File Always Exists

`src/settings_loader.py`'s `load_settings` assumes the config file always
exists at the given path and opens it with no existence check or fallback.

## Expected agent finding

- **Assumption:** the config file always exists at the given path.
- **Evidence:** `src/settings_loader.py` (`load_settings`).
- **Counterexample:** the config file is missing (deleted, wrong path, fresh install).
- **Expected failure:** `FileNotFoundError`.
