# case_005 — UTC Timezone Assumption

`src/scheduler.py`'s `is_event_upcoming` assumes every `event_time` passed in
is a timezone-aware UTC datetime, and compares it directly to
`datetime.now(timezone.utc)` with no normalization.

## Expected agent finding

- **Assumption:** event timestamps are always timezone-aware UTC datetimes.
- **Evidence:** `src/scheduler.py` (`is_event_upcoming`).
- **Counterexample:** caller passes a naive local datetime (no `tzinfo`).
- **Expected failure:** `TypeError: can't compare offset-naive and offset-aware datetimes`.
