# case_009 — Username Uniqueness

`src/registry.py`'s `UserRegistry.register` assumes usernames are always
unique at the call site and never checks for an existing entry before
writing, so a second registration under the same username silently
overwrites the first account's email — a takeover vector, not a crash.

## Expected agent finding

- **Assumption:** usernames passed to `register` are always unique.
- **Evidence:** `src/registry.py` (`UserRegistry.register`).
- **Counterexample:** registering `"alice"` twice with different emails.
- **Expected failure:** the second registration silently overwrites the first, with no conflict error.
