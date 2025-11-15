Got it — here’s a **simplified** `./instructions/testing.md` for Copilot.
(Explicit: AI may run tests. **Do not write or run destructive tests.**)

---

# Testing Instructions (Azure Function App) — Pytest

**Audience:** GitHub Copilot / AI assistants
**Authority:** You **may run tests** and collect results.
**Guardrail:** Do **not** modify code unless explicitly approved.
**Hard rule:** **Don’t write destructive tests. Don’t run destructive tests.**

## Test Scope

* **Library tests (unit):** `./functions/[MODULE].py` — pure logic, mock external IO.
* **Live endpoint tests (safe only):** hit exposed HTTP endpoints (health/read-only).

  * No reporting, no deletes, no state-changing actions.

## Markers

* `unit` — fast library tests.
* `live` — safe, read-only endpoint checks.
* `endpoint` — tests that call the actual HTTP endpoint (follow the AbuseIPDB pattern).

> Do **not** create or use any `destructive` marker. Destructive tests are **forbidden**.

## Testing Pattern

* **Follow the AbuseIPDB pattern:** Use `@pytest.mark.endpoint` and call the actual HTTP endpoint for tests.
* Endpoint tests should make real HTTP requests to the running function app.
* These tests verify the full integration including routing, request parsing, and response formatting.

## Environment

* Configure via env vars (e.g., `APP_BASE_URL`, `APP_AUTH_TOKEN`).
* If missing, **skip** live tests with a clear reason.

## Commands

```bash
# Units only
pytest -m "unit" -q

# Units + safe live endpoint tests
pytest -m "unit or live" -q
```

## What to Test (minimum)

* **Unit:** core logic, error handling, retries/backoff (mocked), serialization, determinism.
* **Live:** health/status endpoint (200), read-only JSON shape, auth behavior (401/403 as expected), idempotent GETs.

## Resolution Loop

1. Run the tests (commands above).
2. Output a **short summary**: passed/failed/skipped + top failing tests with one-line reasons.
3. Ask: **Approve fixes?**

   * If approved, make the smallest changes, re-run tests.
   * If not approved, stop.
4. Repeat until all tests pass.

## Reporting (brief)

* `passed=X, failed=Y, skipped=Z (unit=…, live=…)`
* Bullet list of failing tests → cause.
* Next step prompt: **Approve fixes / Stop**.

## CI Default

* Run `pytest -m "unit or live"`.
* Fail on any error.
* No destructive tests allowed.

---