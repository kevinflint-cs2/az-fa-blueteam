---
description: 'Apply Python coding conventions and style guidelines for consistent code quality'
mode: 'ask'
---

# Python Coding Standards — Style and Documentation

Apply consistent Python coding conventions following PEP 8 and best practices for readable, maintainable, and well-documented code in this Azure Functions repository.

## Mission

Ensure all Python code adheres to established conventions for naming, formatting, type hints, docstrings, and error handling. Promote code clarity and maintainability through consistent style and comprehensive documentation.

## Scope & Preconditions

- **Target Files:** All Python files (`**/*.py`) in the repository
- **Style Guide:** PEP 8 (enforced via Ruff)
- **Type Checking:** MyPy with strict settings
- **Docstring Format:** PEP 257 conventions
- **Testing Framework:** pytest with type-annotated test functions

## Inputs

When reviewing or generating Python code:
- **Function signature:** Name, parameters, return type
- **Purpose:** What the function accomplishes
- **Context:** Module-level context and dependencies
- **Edge cases:** Expected error conditions and boundary cases

## Core Conventions

### Function Design

**Descriptive Names:**
- Use verb phrases for functions: `calculate_area()`, `fetch_data()`, `validate_input()`
- Use noun phrases for classes: `DataProcessor`, `APIClient`, `ConfigManager`
- Use snake_case for functions and variables
- Use PascalCase for classes

**Type Hints:**
- Always provide type hints for function parameters and return values
- Use `typing` module for complex types: `List[str]`, `Dict[str, int]`, `Optional[float]`
- Use union syntax for multiple types: `str | None` (Python 3.10+)

```python
from typing import Dict, List, Optional, Any

def process_results(
    data: List[Dict[str, Any]],
    filter_key: Optional[str] = None
) -> Dict[str, List[Any]]:
    """Process and group results by key."""
    # Implementation
    pass
```

**Docstrings:**
- Required for all public functions, classes, and modules
- Follow PEP 257 conventions
- Include Args, Returns, Raises sections

```python
def calculate_area(radius: float) -> float:
    """
    Calculate the area of a circle given the radius.

    Args:
        radius: The radius of the circle in units.

    Returns:
        The area of the circle, calculated as π × radius².

    Raises:
        ValueError: If radius is negative.
    """
    if radius < 0:
        raise ValueError("Radius cannot be negative")
    import math
    return math.pi * radius ** 2
```

### Code Organization

**Function Complexity:**
- Keep functions focused on single responsibility
- Break complex functions into smaller helper functions
- Aim for functions under 50 lines when possible

**Import Organization:**
```python
# Standard library imports
import os
import json
from typing import Dict, Any

# Third-party imports
import requests
from azure import functions as func

# Local application imports
from functions import helper_module
```

**Module Docstrings:**
```python
"""
module_name.py - Brief module purpose

Detailed description of module capabilities, external dependencies,
and integration points.
"""
```

### Code Style (PEP 8)

**Indentation:**
- Use 4 spaces per indentation level
- Never mix tabs and spaces

**Line Length:**
- Maximum 79 characters for code
- Maximum 72 characters for docstrings/comments

**Blank Lines:**
- Two blank lines between top-level functions and classes
- One blank line between methods within a class
- Use blank lines sparingly within functions to separate logical sections

**Naming Conventions:**
```python
# Variables and functions
user_name = "John"
def calculate_total(): pass

# Constants
MAX_RETRIES = 3
API_TIMEOUT = 30

# Classes
class UserAccount: pass

# Private/internal (single underscore)
def _internal_helper(): pass
_config_cache = {}
```

**String Quotes:**
- Use double quotes for strings: `"Hello"`
- Use single quotes for dict keys when convenient: `{'key': 'value'}`
- Be consistent within each file

### Error Handling

**Explicit Exception Handling:**
```python
def fetch_data(url: str) -> Dict[str, Any]:
    """
    Fetch data from URL with proper error handling.

    Args:
        url: The URL to fetch data from.

    Returns:
        Parsed JSON response.

    Raises:
        ValueError: If URL is invalid or empty.
        requests.exceptions.RequestException: If request fails.
    """
    if not url:
        raise ValueError("URL cannot be empty")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        raise requests.exceptions.RequestException("Request timed out")
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Failed to fetch data: {e}")
```

**Early Validation:**
```python
def process_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process user data with early validation."""
    # Validate early, fail fast
    if not data:
        raise ValueError("Data cannot be empty")
    if "user_id" not in data:
        raise ValueError("Missing required field: user_id")
    if not isinstance(data["user_id"], int):
        raise ValueError("user_id must be an integer")

    # Process validated data
    result = {"processed": True, "user_id": data["user_id"]}
    return result
```

**Context Managers:**
```python
# Use context managers for resource management
with open("data.json", "r") as f:
    data = json.load(f)

# Custom context managers for cleanup
from contextlib import contextmanager

@contextmanager
def temporary_config(new_config: Dict[str, Any]):
    """Temporarily override configuration."""
    old_config = get_config()
    set_config(new_config)
    try:
        yield
    finally:
        set_config(old_config)
```

### Edge Cases and Defensive Programming

**Handle Empty Inputs:**
```python
def sum_values(numbers: List[float]) -> float:
    """Sum a list of numbers, handling edge cases."""
    if not numbers:
        return 0.0
    return sum(numbers)
```

**Validate Input Types:**
```python
def format_name(first: str, last: str) -> str:
    """Format full name from components."""
    if not isinstance(first, str) or not isinstance(last, str):
        raise TypeError("Both first and last must be strings")
    return f"{first} {last}".strip()
```

**Boundary Conditions:**
```python
def paginate_results(
    items: List[Any],
    page: int,
    page_size: int
) -> List[Any]:
    """
    Return paginated subset of items.

    Args:
        items: Full list of items.
        page: Page number (1-indexed).
        page_size: Number of items per page.

    Returns:
        Items for the requested page.

    Raises:
        ValueError: If page or page_size is invalid.
    """
    if page < 1:
        raise ValueError("Page must be >= 1")
    if page_size < 1:
        raise ValueError("Page size must be >= 1")

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    # Handle out-of-bounds gracefully
    if start_idx >= len(items):
        return []

    return items[start_idx:end_idx]
```

### Comments and Documentation

**When to Comment:**
```python
# Good: Explain WHY, not WHAT
# Cache results to avoid repeated API calls during retry logic
_result_cache: Dict[str, Any] = {}

# Bad: Redundant comment
# Increment counter by 1
counter += 1
```

**Algorithm Explanations:**
```python
def find_median(numbers: List[float]) -> float:
    """
    Find the median value using quickselect algorithm.

    The quickselect algorithm provides O(n) average time complexity
    for finding the k-th smallest element, which is more efficient
    than full sorting for large datasets.

    Args:
        numbers: List of numeric values.

    Returns:
        The median value.
    """
    # Implementation with inline comments for complex logic
    pass
```

**TODO Comments:**
```python
# TODO(username): Implement caching layer for frequently accessed data
# FIXME: Handle edge case where API returns null values
# NOTE: This assumes the API response format remains stable
```

### Testing Conventions

**Test Function Names:**
```python
# Descriptive test names following pattern: test_<function>_<scenario>
def test_calculate_area_positive_radius():
    """Test area calculation with valid positive radius."""
    result = calculate_area(5.0)
    assert result == pytest.approx(78.54, rel=0.01)

def test_calculate_area_negative_radius_raises_error():
    """Test that negative radius raises ValueError."""
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_area(-1.0)

def test_calculate_area_zero_radius():
    """Test area calculation with zero radius."""
    result = calculate_area(0.0)
    assert result == 0.0
```

**Test Documentation:**
```python
@pytest.mark.mock
def test_handle_request_with_missing_api_key():
    """
    Test that missing API key raises appropriate error.

    This test verifies that the function properly validates
    environment configuration before attempting API calls.
    """
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ValueError, match="API_KEY not configured"):
            handle_request({"value": "test"})
```

## Code Quality Workflow

### Pre-commit Checks

Before committing code:
1. **Format:** `ruff format .`
2. **Lint:** `ruff check . --fix`
3. **Type check:** `mypy . --config-file mypy.ini`
4. **Test:** `pytest -vv`

### Automated Enforcement

Pre-commit hooks automatically enforce:
- Ruff formatting and linting
- MyPy type checking
- Detect-secrets for credential scanning

## Common Patterns

### Configuration Management

```python
import os
from typing import Optional

def get_config_value(
    key: str,
    default: Optional[str] = None,
    required: bool = False
) -> Optional[str]:
    """
    Retrieve configuration value from environment.

    Args:
        key: Environment variable name.
        default: Default value if not found.
        required: Whether to raise error if missing.

    Returns:
        Configuration value or default.

    Raises:
        ValueError: If required=True and key not found.
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise ValueError(f"Required configuration missing: {key}")
    return value
```

### Retry Logic

```python
import time
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    base_delay: float = 1.0
) -> T:
    """
    Retry function with exponential backoff.

    Args:
        func: Function to retry.
        max_attempts: Maximum number of attempts.
        base_delay: Initial delay between retries.

    Returns:
        Result of successful function call.

    Raises:
        Exception: If all retry attempts fail.
    """
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    raise RuntimeError("Retry logic failed unexpectedly")
```

### API Response Parsing

```python
def parse_api_response(
    response: requests.Response
) -> Dict[str, Any]:
    """
    Parse and validate API response.

    Args:
        response: HTTP response object.

    Returns:
        Parsed JSON data.

    Raises:
        ValueError: If response is invalid JSON.
        requests.exceptions.HTTPError: If status code indicates error.
    """
    response.raise_for_status()

    try:
        data = response.json()
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in response: {e}")

    # Validate expected structure
    if not isinstance(data, dict):
        raise ValueError("Expected JSON object in response")

    return data
```

## Quality Assurance Checklist

- [ ] All functions have descriptive names and type hints
- [ ] Docstrings present for public functions (Args, Returns, Raises)
- [ ] Input validation performed early with appropriate exceptions
- [ ] Edge cases handled (empty inputs, boundary conditions)
- [ ] Imports organized (stdlib, third-party, local)
- [ ] Lines under 79 characters
- [ ] Consistent indentation (4 spaces)
- [ ] Comments explain WHY, not WHAT
- [ ] Test functions have clear, descriptive names
- [ ] Code passes `ruff check` and `ruff format`
- [ ] Code passes `mypy` type checking
- [ ] No hardcoded secrets or credentials

## Related Resources

- [PEP 8 Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 Docstring Conventions](https://peps.python.org/pep-0257/)
- [Python Type Hints (PEP 484)](https://peps.python.org/pep-0484/)
- [Implementation Pattern](./implementation-pattern.prompt.md) — Module structure
- [Testing Guidelines](./testing.prompt.md) — Test writing conventions
