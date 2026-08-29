# case_004 — External API Always Returns JSON

`src/weather_client.py`'s `fetch_weather` assumes the weather API always
responds with a parseable JSON body and calls `response.json()` with no
try/except or content-type check.

## Expected agent finding

- **Assumption:** the external weather API always returns valid JSON.
- **Evidence:** `src/weather_client.py` (`fetch_weather`).
- **Counterexample:** API returns an HTML error page (e.g. 503) instead of JSON.
- **Expected failure:** `ValueError` (or `json.JSONDecodeError`) from `.json()`.
