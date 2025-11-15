---
description: 'Execute pytest test suites with proper markers and validation for Azure Functions'
mode: 'agent'
tools: ['run_terminal']
---

# Testing — Pytest Execution and Validation

Execute comprehensive test suites for Azure Functions modules using pytest with proper markers, environment configuration, and iterative fix validation. Never create or run destructive tests.

## Mission

Run test suites to validate module functionality through unit tests (mocked), endpoint tests (HTTP integration), and safe live tests (read-only API calls). Provide clear test results and guide fix approval workflow.

## Scope & Preconditions

- **Test Framework:** pytest with markers (`mock`, `endpoint`, `live`)
- **Test Location:** `tests/` directory with naming pattern `test_[module].py`
- **Environment:** Virtual environment activated (`.venv/bin/activate`)
- **Authority:** May run tests and collect results; cannot modify code without approval
- **Hard Rule:** Never write or execute destructive tests (no data modification, deletion, or reporting)

## Inputs

- **Test Scope:** Which markers to run (`mock`, `endpoint`, `live`, or combinations)
- **Module Filter:** Specific module(s) to test (optional)
- **Environment Variables:** Configuration for live tests (API keys, base URLs)
- **Fix Approval:** User authorization required before modifying code

## Test Markers

### @pytest.mark.mock
- **Purpose:** Unit tests with mocked external dependencies
- **Characteristics:**
  - Fast execution (no network I/O)
  - Mock HTTP calls using `unittest.mock` or `responses`
  - Test business logic in isolation
  - Always included in test runs

### @pytest.mark.endpoint
- **Purpose:** HTTP endpoint integration tests
- **Characteristics:**
  - Call actual HTTP endpoints (local or deployed)
  - Test full request/response cycle
  - Verify routing, parsing, error handling
  - Follow AbuseIPDB pattern for structure

### @pytest.mark.live
- **Purpose:** Safe, read-only tests against real external APIs
- **Characteristics:**
  - Require valid API keys in environment
  - Only safe, idempotent operations (GET requests, health checks)
  - Skip gracefully if credentials missing
  - No state-changing actions (no POST/PUT/DELETE for data modification)

## Testing Patterns

### Unit Test Pattern (Mock)

```python
import pytest
from unittest.mock import patch, Mock

@pytest.mark.mock
def test_handle_request_success():
    """Test successful request handling with mocked API."""
    payload = {"ip": "8.8.8.8"}

    with patch("module_name._call_external_api") as mock_api:
        mock_api.return_value = {"score": 0, "reports": []}
        result = module_name.handle_request(payload)

    assert result["status"] == "ok"
    assert "result" in result
    mock_api.assert_called_once()

@pytest.mark.mock
def test_handle_request_missing_parameter():
    """Test validation of required parameters."""
    payload = {}

    with pytest.raises(ValueError, match="missing.*parameter"):
        module_name.handle_request(payload)

@pytest.mark.mock
def test_handle_request_api_timeout():
    """Test handling of API timeout errors."""
    payload = {"ip": "8.8.8.8"}

    with patch("module_name._call_external_api") as mock_api:
        mock_api.side_effect = requests.exceptions.Timeout()

        with pytest.raises(requests.exceptions.RequestException):
            module_name.handle_request(payload)
```

### Endpoint Test Pattern

```python
import pytest
import requests

@pytest.mark.endpoint
def test_endpoint_success(base_url):
    """Test successful endpoint call."""
    response = requests.get(
        f"{base_url}/api/module/check",
        params={"ip": "8.8.8.8"},
        timeout=30
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "result" in data

@pytest.mark.endpoint
def test_endpoint_missing_parameter(base_url):
    """Test endpoint with missing required parameter."""
    response = requests.get(
        f"{base_url}/api/module/check",
        timeout=30
    )

    assert response.status_code == 400
    data = response.json()
    assert data["status"] == "error"
    assert "error" in data

@pytest.mark.endpoint
def test_endpoint_invalid_value(base_url):
    """Test endpoint with invalid parameter value."""
    response = requests.get(
        f"{base_url}/api/module/check",
        params={"ip": "invalid"},
        timeout=30
    )

    assert response.status_code == 400
```

### Live Test Pattern

```python
import pytest
import os

@pytest.mark.live
def test_live_api_call():
    """Test live API with real credentials."""
    api_key = os.getenv("MODULE_API_KEY")
    if not api_key:
        pytest.skip("MODULE_API_KEY not configured")

    # Only safe, read-only operations
    payload = {"value": "example.com"}
    result = module_name.handle_request(payload)

    assert result["status"] == "ok"
    assert "result" in result

@pytest.mark.live
def test_live_health_check():
    """Test API health/status endpoint (safe, idempotent)."""
    api_key = os.getenv("MODULE_API_KEY")
    if not api_key:
        pytest.skip("MODULE_API_KEY not configured")

    # Health checks are always safe
    response = requests.get(
        "https://api.example.com/health",
        headers={"Authorization": f"Bearer {api_key}"}
    )

    assert response.status_code in [200, 204]
```

## Test Execution Commands

### Run Unit Tests Only
```bash
pytest -m "mock" -vv
```

### Run Endpoint Tests
```bash
pytest -m "endpoint" -vv
```

### Run Unit + Endpoint Tests
```bash
pytest -m "mock or endpoint" -vv
```

### Run All Safe Tests (Including Live)
```bash
pytest -m "mock or endpoint or live" -vv
```

### Run Specific Module Tests
```bash
pytest tests/test_module_name.py -vv
```

### Run with Coverage
```bash
pytest --cov=functions --cov-report=term-missing -vv
```

## Environment Configuration

### Required for Live Tests
```bash
# Set API keys using Azure Functions CLI
func settings add MODULE_API_KEY "your-key-here"  # pragma: allowlist secret

# Or export for pytest execution
export MODULE_API_KEY="your-key-here"  # pragma: allowlist secret
export APP_BASE_URL="http://localhost:7071"
```

### Skip Tests Gracefully
```python
import os
import pytest

# Skip if environment not configured
@pytest.mark.live
def test_requires_credentials():
    """Test that requires live credentials."""
    if not os.getenv("API_KEY"):
        pytest.skip("API_KEY not configured")

    # Test implementation
```

## Resolution Workflow

### Step 1: Execute Tests

Run the appropriate test suite based on scope:

```bash
# Activate virtual environment first
source .venv/bin/activate

# Run tests with verbose output
pytest -m "mock or endpoint" -vv
```

### Step 2: Analyze Results

Collect and summarize:
- **Total:** passed, failed, skipped counts
- **By Marker:** breakdown by `mock`, `endpoint`, `live`
- **Failures:** test names and failure reasons (one-line each)

Example summary format:
```
Test Results:
✅ 42 passed
❌ 2 failed
⏭️  5 skipped

Failures:
1. test_handle_request_invalid_ip - AssertionError: Expected 400, got 500
2. test_endpoint_timeout - requests.exceptions.Timeout: Request exceeded 30s

Skipped:
- 5 live tests (API_KEY not configured)
```

### Step 3: Propose Fixes

For each failing test:
1. **Explain root cause** in plain language
2. **Suggest specific fix** (what needs to change and why)
3. **Request approval** before implementing

Example:
```
Fix Proposal for test_handle_request_invalid_ip:

Root Cause:
The function is not validating IP address format before calling the API,
causing the external service to return 500 instead of our validation
returning 400.

Suggested Fix:
Add IP address format validation at the start of handle_request():
- Use ipaddress.ip_address() to validate format
- Raise ValueError("Invalid IP address format") if validation fails
- This will trigger 400 response in function_app.py

Approve fix? (yes/no)
```

### Step 4: Apply Approved Fixes

After receiving approval:
1. Implement the minimal fix required
2. Re-run the affected test(s)
3. Verify fix resolves the issue
4. Continue with remaining failures

### Step 5: Iterate Until Clean

Repeat steps 2-4 until all tests pass:
- Process one failure at a time
- Re-run full test suite after each fix
- Provide updated summary after each iteration

## Minimum Test Coverage

Every module must include tests for:

### Happy Path
- ✅ Valid input → successful response
- ✅ Expected output structure and data types
- ✅ Business logic correctness

### Input Validation
- ✅ Missing required parameters → `ValueError` / 400
- ✅ Invalid parameter types → `ValueError` / 400
- ✅ Empty or null inputs → appropriate handling
- ✅ Boundary values (min/max, edge cases)

### Error Handling
- ✅ External API errors → `RequestException` / 502
- ✅ Authentication failures → 401
- ✅ Timeout scenarios → graceful degradation
- ✅ Unexpected errors → 500

### HTTP Endpoint Integration
- ✅ Correct HTTP method handling (GET/POST)
- ✅ Query parameter parsing
- ✅ JSON body parsing
- ✅ Response status codes
- ✅ Response content type (application/json)

## Reporting Format

### Brief Summary (After Each Run)

```
=== Test Results ===
Status: PASS / FAIL
Passed: X
Failed: Y
Skipped: Z

Markers:
- mock: X passed, Y failed
- endpoint: X passed, Y failed
- live: X passed, Z skipped

Next Step: [Continue to Phase 6 / Fix failures]
```

### Detailed Failure Report (When Failures Exist)

```
=== Failing Tests ===

1. test_function_name_scenario (tests/test_module.py::line)
   Reason: AssertionError - Expected X but got Y
   Fix: [Specific proposed change]

2. test_another_failure (tests/test_module.py::line)
   Reason: ValueError - Missing required parameter
   Fix: [Specific proposed change]

Approve fixes? (yes/no/specific)
```

## CI/CD Integration

### Default CI Pipeline
```bash
# Run safe tests only
pytest -m "mock or endpoint" -vv --junitxml=test-results.xml

# Fail pipeline on any test failure
# Exit code 0 = all pass, non-zero = failures
```

### Pre-deployment Validation
```bash
# Full test suite including live tests
pytest -m "mock or endpoint or live" -vv

# Ensure no warnings
pytest -vv --strict-warnings
```

## Quality Assurance Checklist

- [ ] Virtual environment activated before running tests
- [ ] All unit tests (mock) pass
- [ ] All endpoint tests pass
- [ ] Live tests pass or skip gracefully if credentials missing
- [ ] No destructive tests present in test suite
- [ ] Test coverage meets minimum requirements (all patterns covered)
- [ ] Flaky tests identified and addressed
- [ ] Tests run in isolation (no dependencies between tests)
- [ ] Test execution time reasonable (< 60 seconds for unit tests)

## Forbidden Practices

### ❌ Never Create Destructive Tests
```python
# FORBIDDEN - Creates/modifies data
@pytest.mark.destructive  # Do not use this marker
def test_create_report():
    """This test creates actual reports - FORBIDDEN."""
    api.create_report(data)  # State-changing operation

# FORBIDDEN - Deletes data
def test_delete_record():
    """This test deletes records - FORBIDDEN."""
    api.delete(record_id)  # Destructive operation
```

### ✅ Only Safe, Read-Only Tests
```python
# SAFE - Read-only query
@pytest.mark.live
def test_query_existing_data():
    """Safe test that only reads data."""
    result = api.get_status()  # Idempotent, read-only
    assert result["status"] == "active"

# SAFE - Health check
@pytest.mark.live
def test_api_health():
    """Safe health check endpoint."""
    response = requests.get("/health")  # No side effects
    assert response.status_code == 200
```

## Validation Steps

After all tests pass:
1. Verify test results in terminal output
2. Check for warnings or deprecation notices
3. Confirm no tests were unexpectedly skipped (unless credentials missing)
4. Review coverage report (if generated)
5. State: "Phase 5 complete. All tests passing. Ready for Phase 6."

## Related Resources

- [Development Process](./development-process.prompt.md) — Seven-phase workflow
- [Implementation Pattern](./implementation-pattern.prompt.md) — Module structure
- [Python Coding Standards](./python-coding.prompt.md) — Code conventions
- [pytest Documentation](https://docs.pytest.org/) — Official pytest guide
