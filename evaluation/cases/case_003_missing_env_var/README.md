# case_003 — Missing Environment Variable

`src/config.py`'s `get_database_url` assumes `DATABASE_URL` is always set and
reads it with `os.environ[...]` instead of `.get()` with a fallback or check.

## Expected agent finding

- **Assumption:** the `DATABASE_URL` environment variable always exists.
- **Evidence:** `src/config.py` (`get_database_url`).
- **Counterexample:** running the app without `DATABASE_URL` set.
- **Expected failure:** `KeyError: 'DATABASE_URL'`.
