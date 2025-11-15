---
description: 'Apply Azure Functions module implementation patterns for consistent code structure'
mode: 'ask'
tools: ['read_file', 'semantic_search']
---

# Implementation Pattern — Azure Functions Python Modules

Apply consistent implementation patterns when adding new enrichment endpoints to this Azure Functions app. Ensure code follows established conventions for structure, error handling, testing, and deployment.

## Mission

Provide a repeatable pattern for implementing new function modules that maintains consistency across the codebase in naming, inputs/outputs, error handling, configuration management, and testing strategy.

## Scope & Preconditions

- **Target Environment:** Azure Functions app (Python) for security enrichment APIs
- **Module Location:** `functions/` directory for business logic
- **Routing Location:** `function_app.py` for HTTP trigger definitions
- **Test Location:** `tests/` directory with pytest markers
- **Prerequisites:**
  - Python virtual environment activated (`.venv`)
  - Dependencies managed via `requirements.txt` and `requirements-dev.txt`
  - Azure Functions Core Tools installed

## Inputs

When implementing a new function module, gather:
- **Module Name:** Snake_case identifier (e.g., `my_service`)
- **API Provider:** External service being integrated (e.g., AbuseIPDB, AlienVault)
- **Endpoint Route:** HTTP path (e.g., `/api/my_service/check`)
- **Input Schema:** Expected parameters (query params or JSON body)
- **Output Schema:** Response structure and status codes
- **API Key Environment Variable:** Name for secret configuration (e.g., `MY_SERVICE_API_KEY`)

## Module Structure Pattern

### File Organization

```
functions/
  my_service.py          # Business logic module
function_app.py          # HTTP route definitions
tests/
  test_my_service.py     # Unit tests (mocked)
  test_my_service_endpoint.py  # HTTP endpoint tests
  test_my_service_live.py      # Live API tests (optional)
```

### Module Template

```python
"""
my_service.py - [Brief module purpose]

Integrates with [External API] to [capability description].
"""

from typing import Dict, Any
import os
import requests


def handle_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle a parsed request payload and return a JSON-serializable dict.

    Args:
        payload: Parsed JSON body or dict of parameters.
                 Required keys: [list required keys]

    Returns:
        Dict with keys:
        - status: 'ok' or 'error'
        - result: Response data (on success)
        - error: Error details (on failure)

    Raises:
        ValueError: If required parameters are missing or invalid.
    """
    # Validate inputs
    if "value" not in payload:
        raise ValueError("missing 'value' parameter")

    # Get API key from environment
    api_key = os.getenv("MY_SERVICE_API_KEY")
    if not api_key:
        raise ValueError("MY_SERVICE_API_KEY not configured")

    # Business logic
    result = _call_external_api(payload["value"], api_key)

    return {"status": "ok", "result": result}


def _call_external_api(value: str, api_key: str) -> Dict[str, Any]:
    """
    Internal function to interact with external API.

    Args:
        value: Input parameter
        api_key: Authentication credential

    Returns:
        Parsed API response

    Raises:
        requests.exceptions.RequestException: On API communication errors
    """
    headers = {"Key": api_key, "Accept": "application/json"}
    response = requests.get(
        "https://api.example.com/endpoint",
        params={"q": value},
        headers=headers,
        timeout=10
    )
    response.raise_for_status()
    return response.json()
```

## HTTP Route Pattern (function_app.py)

```python
@app.route(route="my_service/check", methods=["GET", "POST"])
def my_service_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    HTTP endpoint for [capability description].

    Query Parameters:
        value: [Description of parameter]

    Returns:
        JSON response with status and result/error
    """
    try:
        # Parse input (query params or JSON body)
        if req.method == "GET":
            payload = {"value": req.params.get("value")}
        else:
            payload = req.get_json()

        # Call module handler
        result = my_service.handle_request(payload)

        return func.HttpResponse(
            json.dumps(result),
            mimetype="application/json",
            status_code=200
        )

    except ValueError as e:
        # Client error (400)
        error = {"status": "error", "error": {"msg": str(e)}}
        return func.HttpResponse(
            json.dumps(error),
            mimetype="application/json",
            status_code=400
        )

    except requests.exceptions.RequestException as e:
        # External API error (502)
        error = {"status": "error", "error": {"msg": f"API error: {str(e)}"}}
        return func.HttpResponse(
            json.dumps(error),
            mimetype="application/json",
            status_code=502
        )

    except Exception as e:
        # Unexpected error (500)
        error = {"status": "error", "error": {"msg": "Internal server error"}}
        return func.HttpResponse(
            json.dumps(error),
            mimetype="application/json",
            status_code=500
        )
```

## Input/Output Contract

### Standard Request Payload

Prefer a single dict payload representing parsed JSON or parameters:

```python
payload = {
    "value": "user-input",
    "option1": True,
    "option2": "setting"
}
```

### Standard Response Shape

**Success:**
```json
{
  "status": "ok",
  "result": {
    "data": "...",
    "metadata": {}
  }
}
```

**Error:**
```json
{
  "status": "error",
  "error": {
    "msg": "Descriptive error message"
  }
}
```

## Error Handling Strategy

### Exception Mapping

| Exception Type | HTTP Status | Use Case |
|---------------|-------------|----------|
| `ValueError` | 400 | Missing or invalid input parameters |
| Authentication/API key errors | 401 | Missing or invalid credentials |
| External API errors | 502 | Upstream service failures |
| Unexpected errors | 500 | Catch-all for unhandled exceptions |

### Implementation Guidelines

1. **Validate early:** Check required parameters at the start of `handle_request()`
2. **Raise specific exceptions:** Use `ValueError` for client errors, custom exceptions for API errors
3. **Map in route handler:** Keep HTTP status code logic in `function_app.py`
4. **Log appropriately:** Use Azure Functions logging for debugging

## Configuration & Secrets Management

### Environment Variables

**Local Development:**
- Non-secret config: Store in `local.settings.json` (gitignored)
- Secret values (API keys): Use Azure Functions Core Tools

```bash
# Add secrets using func CLI (keeps them out of version control)
func settings add MY_SERVICE_API_KEY "your-api-key-here"
```

**Azure Deployment:**
- Configure via Application Settings in Azure Portal
- Use Key Vault references for production secrets

### Common Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `ABUSEIPDB_API_KEY` | AbuseIPDB authentication | `abc123...` |
| `ALIENVAULT_API_KEY` | AlienVault OTX authentication | `xyz789...` |
| `URLSCAN_API_KEY` | URLScan.io authentication | `def456...` |

### Reading Configuration

```python
import os

api_key = os.getenv("MY_SERVICE_API_KEY")
if not api_key:
    raise ValueError("MY_SERVICE_API_KEY not configured")
```

## Virtual Environment Management

**Critical:** Always ensure the virtual environment is activated before running Python commands.

### Activation

```bash
# Linux/macOS/Dev Container
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### Verification

```bash
# Check which Python is active
which python

# Should show: /path/to/project/.venv/bin/python
```

### VS Code Integration

The Azure Functions extension uses `${config:azureFunctions.pythonVenv}` setting to automatically activate the virtual environment. Verify this is configured in `.vscode/settings.json`.

## Testing Requirements

### Test Categories

1. **Unit Tests** (`test_[module].py`):
   - Mock external HTTP calls
   - Test business logic in isolation
   - Use `@pytest.mark.mock` marker
   - Fast execution (no network)

2. **Endpoint Tests** (`test_[module]_endpoint.py`):
   - Call actual HTTP endpoints
   - Test full request/response cycle
   - Use `@pytest.mark.endpoint` marker
   - Verify routing and error handling

3. **Live Tests** (`test_[module]_live.py`):
   - Call real external APIs
   - Use `@pytest.mark.live` marker
   - Only safe, read-only operations
   - Skip if API keys not configured

### Minimum Test Coverage

- ✅ Happy path (valid input → success response)
- ✅ Missing required parameter → 400 error
- ✅ Empty/null inputs → appropriate handling
- ✅ External API error simulation → 502 error
- ✅ Authentication failure → 401 error

### Example Test Structure

```python
import pytest
from unittest.mock import patch, Mock

@pytest.mark.mock
def test_handle_request_success():
    """Test successful request handling."""
    payload = {"value": "test"}
    with patch("my_service._call_external_api") as mock_api:
        mock_api.return_value = {"data": "result"}
        result = my_service.handle_request(payload)
        assert result["status"] == "ok"
        assert "result" in result

@pytest.mark.mock
def test_handle_request_missing_value():
    """Test validation of required parameters."""
    payload = {}
    with pytest.raises(ValueError, match="missing 'value' parameter"):
        my_service.handle_request(payload)
```

## Code Quality Standards

### Linting (Ruff)

```bash
# Check for issues
ruff check .

# Auto-fix safe issues
ruff check . --fix

# Format code
ruff format .
```

### Type Checking (Mypy)

```bash
# Run type checker
mypy . --config-file mypy.ini --check-untyped-defs
```

### Pre-commit Integration

Hooks automatically run linting and type checking before each commit. Ensure hooks are installed:

```bash
pre-commit install
```

## Dependency Management

### Adding Runtime Dependencies

1. Add package to `requirements.txt`:
   ```
   requests>=2.31.0
   ```

2. Install in virtual environment:
   ```bash
   pip install -r requirements.txt
   ```

### Adding Development Dependencies

1. Add package to `requirements-dev.txt`:
   ```
   pytest>=8.0.0
   ```

2. Install in virtual environment:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Deployment Checklist

Before submitting a pull request:

- [ ] Tests added and passing locally: `pytest -vv`
- [ ] Linting passes: `ruff check . && ruff format .`
- [ ] Type checking passes: `mypy .`
- [ ] Dependencies updated in `requirements.txt` if needed
- [ ] Environment variables documented in module docstring
- [ ] README updated with new endpoint information
- [ ] Module documentation created in `./docs/modules/`
- [ ] Example documentation created in `./docs/examples/`

## Deployment Process

### Staging Deployment

```bash
# Create deployment package
./deploy_staging.sh

# Uploads function app to Azure
# Ensure secrets are configured in Azure Application Settings
```

### Production Considerations

- Configure Application Settings in Azure Portal
- Use Key Vault for sensitive credentials
- Enable Application Insights for monitoring
- Set up appropriate CORS policies
- Configure authentication/authorization as needed

## AI-Specific Instructions

When prompting an AI to implement a new function, provide:

1. **Module specification:**
   - Target file path: `functions/my_service.py`
   - HTTP route: `/api/my_service/action`

2. **Input/output schemas:**
   - Example input JSON with all parameters
   - Expected output JSON with success/error cases

3. **External integration:**
   - API endpoint URL
   - Authentication method
   - Environment variable name for API key

4. **Testing requirements:**
   - Specific test cases to cover
   - Example mocked API responses

5. **Documentation needs:**
   - Module purpose and capabilities
   - curl examples for common use cases

## Related Resources

- [Development Process](./development-process.prompt.md) — Seven-phase workflow
- [Python Coding Standards](./python-coding.prompt.md) — Style and documentation
- [Testing Guidelines](./testing.prompt.md) — Test execution patterns
- [Linting & Type Checking](./linting-typechecking.prompt.md) — Code quality validation
- [Documentation Standards](./documentation.prompt.md) — Documentation requirements
