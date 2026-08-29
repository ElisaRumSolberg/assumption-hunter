# case_001 — Nullable Email

`src/users.py` assumes every `User` has a non-null `email`. `normalize_email`
calls `.lower()` directly on `user.email` with no null check.

## Expected agent finding

- **Assumption:** every user has a non-null email address.
- **Evidence:** `src/users.py` (`normalize_email`, `build_display_name`).
- **Counterexample:** `User(name="Ali", email=None)`.
- **Expected failure:** `AttributeError: 'NoneType' object has no attribute 'lower'`.

Run `pytest test_users.py` to see the failure reproduced deliberately via
`pytest.raises`.
