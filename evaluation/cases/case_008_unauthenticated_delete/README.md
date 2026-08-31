# case_008 — Caller Always Authenticated

`src/documents.py`'s `delete_document` assumes every caller is already
authenticated and authorized, and performs no check on `request` before
deleting. This is a security assumption, not a crash: the "failure" is that
the operation silently *succeeds* when it should have been denied.

## Expected agent finding

- **Assumption:** the caller is always authenticated/authorized before `delete_document` runs.
- **Evidence:** `src/documents.py` (`delete_document`).
- **Counterexample:** an anonymous/unauthenticated request.
- **Expected failure:** the document is deleted with no auth check — a silent security failure, not an exception.
