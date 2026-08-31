# case_010 — Multiple Interacting Assumptions

`src/report_scheduler.py`'s `schedule_report` makes two independent hidden
assumptions in the same function: the environment variable
`REPORT_TIMEZONE` is always set, and `run_at` is always a timezone-aware
datetime. Tests both a detector's ability to find more than one assumption
in one file and to tell them apart (different categories, different
failures).

## Expected agent finding

- **A1 — environment:** `REPORT_TIMEZONE` is always set. Missing it raises `KeyError`.
- **A2 — time:** `run_at` is always timezone-aware. A naive datetime raises `TypeError` when compared to `datetime.now(timezone.utc)`.

Both are evidenced by the same file, `src/report_scheduler.py`.
