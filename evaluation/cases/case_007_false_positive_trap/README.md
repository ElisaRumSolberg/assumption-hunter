# case_007 — False-Positive Trap (Guarded Assumption)

This is the "challenging case" required by the hackathon rubric. The file
contains two lookalike functions:

- `format_billing_email` — looks like the nullable-email pattern from
  `case_001`, but is **already guarded** (`if not user.email: ...`). This is
  the trap: a system that pattern-matches on "`.email` accessed without an
  obvious null check nearby" will misfire here.
- `format_shipping_label` — the real, unguarded assumption: every user has a
  complete `address`.

## Expected agent finding

- **Real assumption (A1):** every user has a complete shipping address.
  **Evidence:** `src/formatting.py` (`format_shipping_label`).
  **Counterexample:** `User(..., address=None)`.
  **Expected failure:** `AttributeError`.
- **Trap (should NOT be reported as a bug):** "every user has a non-null
  email address" — `format_billing_email` already handles `email is None`
  via its fallback string, so flagging this as an unverified risk is a false
  positive.

A system that reports both the real assumption **and** the trap as
equally risky has not actually checked evidence — it pattern-matched on
surface similarity to case_001.
