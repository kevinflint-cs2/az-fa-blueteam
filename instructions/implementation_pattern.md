## Implementation patterns for Azure Functions (Python)

This document describes the recommended implementation patterns for adding new enrichment endpoints to this Azure Functions app. It is intended for human contributors and for automated agents (AI) that generate code for the repository.

### Purpose
- Provide a concise, repeatable pattern for implementing new functions.
- Ensure consistency across modules: naming, inputs/outputs, error handling, tests, and deployment.

### Where to add code
- Function logic modules live under `functions/`.
- HTTP trigger routing lives in `function_app.py`.
- Tests go in `tests/` with pytest; use markers `mock` for unit tests and `live` for tests that call real APIs.

### Module pattern (recommended)
- File name: `snake_case`, e.g. `functions/my_service.py`.
- Module purpose: implement a cohesive capability (single API provider or closely related set of operations).
- Exports:
  - One or more small business-logic functions (pure or thin I/O adapters).
  - A clear entrypoint with a predictable signature, e.g. `def handle_request(payload: dict) -> dict`.

Example module skeleton:

```python
from typing import Dict, Any

def handle_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Handle a parsed request payload and return a JSON-serializable dict.

    Inputs
    - payload: parsed JSON body or a dict of parameters.

    Outputs
    - dict with keys: 'status', 'result' or 'error'
    """
    if "value" not in payload:
        raise ValueError("missing 'value' parameter")

    # Business logic
    result = {"echo": payload["value"]}

    return {"status": "ok", "result": result}
```

### How `function_app.py` should call modules
- Parse request body and/or query params into a plain dict.
- Call the module entrypoint (e.g., `handle_request`).
- Map exceptions to HTTP responses:
  - `ValueError` or invalid input -> HTTP 400
  - Authentication / missing API key -> HTTP 401/403 as appropriate
  - Any other unexpected errors -> HTTP 500
- Return the module's result as JSON.

### Inputs and outputs (contract)
- Inputs: prefer a single dict payload representing parsed JSON or parameters. This reduces boilerplate and makes testing easier.
- Outputs: JSON-serializable dict with either a `result` (on success) or an `error` object, and an explicit `status` string.

Minimal response shape examples:

Success
```json
{ "status": "ok", "result": { ... } }
```

Error
```json
{ "status": "error", "error": { "msg": "explanation" } }
```

### Error handling
- Validate inputs early and raise `ValueError` for client errors.
- Raise specific exceptions for authentication or external API errors when helpful.
- Keep `function_app.py` responsible for HTTP mapping and logging.

### Secrets and configuration
- Do not hardcode API keys. Read them from environment variables. For local development use `local.settings.json` (ignored by git) or `func settings add`.
- Common env var names in this project: `ABUSEIPDB_API_KEY`, `ALIENVAULT_API_KEY`.

### Testing
- Add unit tests under `tests/` named `test_<module>.py`.
- Mock external HTTP calls for unit tests (use `pytest-mock` or `responses`/`requests-mock`).
- Mark live integration tests with `@pytest.mark.live` and exclude them from default CI runs.
- Example test cases to include:
  - happy path
  - missing required parameter
  - empty list inputs
  - simulated external API error (HTTP 429/500)

### Linting and types
- Follow repo style: `ruff` and `mypy` are used in this project.
- Add type hints for public functions and maintain readable docstrings.

### Adding dependencies
- Update `requirements.txt` when adding runtime dependencies.
- Update `requirements-dev.txt` for test/dev tools if needed.

### Deployment
- Use `./deploy_staging.sh` to produce a zip for Azure Function deployment. Ensure secrets are provided in Azure Application Settings.

### Checklist before PR
- Tests added and passing locally for changed modules.
- `ruff` pass locally.
- `requirements.txt` updated if necessary.
- README updated if adding new user-visible endpoints.

### AI-specific instructions (what to provide when asking an AI to add a function)
When prompting an AI to implement a new function, include:
- target module path and file name (e.g., `functions/my_service.py`)
- the route or endpoint to add in `function_app.py` (e.g., `/api/my_service/action`)
- example input JSON and query param schema
- expected output JSON shape and error semantics
- any external API endpoints and the name of the env var for the API key
- whether to add unit tests (and examples of mocked responses)

---