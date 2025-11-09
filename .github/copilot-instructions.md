# GitHub Copilot Instructions for az-fa-blueteam

## Project Overview

This is a lightweight Azure Function App (Python) that provides on-demand blue-team enrichment endpoints for security operations. The app integrates with public APIs like AbuseIPDB, AlienVault OTX, and other threat intelligence services to accelerate triage, hunting, and automation.

## Development Environment Setup

### Prerequisites
- Python 3.8+
- Azure Functions Core Tools
- Virtual environment for dependency isolation

### Initial Setup
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Local Development
Start the Azure Functions host:
```bash
func start
```

## Code Style and Conventions

### Python Style
- Follow PEP 8 conventions
- Use type annotations for all function parameters and return values
- Include docstrings for all functions, especially public API endpoints
- Use meaningful variable names that reflect the domain (e.g., `ip`, `file_hash`, `domain`)

### Code Organization
- **`function_app.py`**: Azure Functions HTTP triggers and routing only
- **`functions/`**: Business logic modules (e.g., `abuseipdb.py`, `alienvault.py`)
- **`tests/`**: Test files with pytest
- Keep HTTP routing logic thin - delegate to functions in `functions/` directory

### Error Handling
- Return HTTP 400 for missing or invalid input parameters
- Return HTTP 500 for API or internal errors
- Provide clear, actionable error messages
- Handle missing API keys gracefully with informative errors

## Testing Requirements

### Test Organization
- **Mock tests** (marked with `@pytest.mark.mock`): Unit tests with mocked HTTP calls
- **Live tests** (marked with `@pytest.mark.live`): Integration tests requiring real API keys

### Running Tests
```bash
# Run only mock tests (default for CI/CD)
pytest -m mock -v

# Run all tests
pytest ./tests -vv

# Run live tests (requires API keys)
pytest -m live -v
```

### Test Guidelines
- Always add mock tests for new endpoints
- Use `unittest.mock` for external API calls
- Test both success and error scenarios
- Validate input parameter handling
- Ensure tests are independent and can run in any order

## Linting and Type Checking

### Required Before Committing
```bash
ruff check .     # Code linting
mypy .          # Type checking
pytest -m mock  # Run mock tests
```

### Standards
- All code must pass `ruff check .` without errors
- All code must pass `mypy .` without errors
- Type hints are required for function signatures
- Fix all linting issues - do not ignore or suppress warnings

## API Integration Guidelines

### Adding New API Endpoints
1. Create a new module in `functions/` (e.g., `functions/newapi.py`)
2. Implement business logic with:
   - Type annotations
   - Docstrings
   - Error handling for missing API keys
   - Clear error messages
3. Add HTTP trigger in `function_app.py`:
   - Support both query params and JSON body
   - Validate required parameters
   - Return appropriate HTTP status codes
4. Add mock tests in `tests/test_newapi.py`
5. Update README.md with endpoint documentation

### API Key Security
- API keys must be environment variables (e.g., `ABUSEIPDB_API_KEY`, `ALIENVAULT_API_KEY`)
- **Never** commit API keys to the repository
- For local development: add keys to `local.settings.json` (already in `.gitignore`)
- For production: set as Application Settings in Azure portal
- Always check for missing API keys and raise clear errors

## Deployment

### Creating Deployment Package
```bash
./deploy_staging.sh
```

This creates `az_fa_blueteam.zip` with only production files (excludes `local.settings.json`, tests, dev dependencies).

### Deployment Methods
- Azure Functions deployment via VS Code extension
- Manual zip deployment to Azure portal
- CI/CD pipeline (if configured)

## Extension Guidelines

When extending this application:
1. **Maintain consistency**: Follow existing patterns in `functions/` modules
2. **Documentation**: Update README.md with new endpoints and usage examples
3. **Testing**: Add comprehensive mock tests, optionally add live tests
4. **Type safety**: Use type annotations and validate with mypy
5. **Security**: Handle API keys properly, validate all inputs
6. **Error handling**: Return appropriate HTTP status codes with clear messages
7. **Minimal dependencies**: Only add new packages if absolutely necessary

## Common Tasks

### Adding a New Threat Intelligence API
1. Research the API documentation and authentication
2. Add API key to environment variable requirements
3. Create `functions/newapi.py` with business logic
4. Add HTTP routes in `function_app.py`
5. Write mock tests in `tests/test_newapi.py`
6. Update README.md with endpoint examples
7. Verify: `ruff check . && mypy . && pytest -m mock`

### Modifying Existing Endpoints
1. Update the relevant function in `functions/` directory
2. Update or add tests to cover the changes
3. Run linting and tests before committing
4. Update README.md if endpoint behavior changes

## Pre-commit Hooks

This repository uses pre-commit hooks. Install them with:
```bash
pre-commit install
```

The hooks will run:
- `detect-secrets`: Prevent committing API keys or secrets
- Other configured checks (see `.pre-commit-config.yaml`)

## Important Notes

- **Do not remove or modify working code** unless fixing a bug or adding a feature
- **Preserve existing test patterns** when adding new tests
- **API keys are sensitive**: Never log, print, or commit them
- **Keep functions focused**: Each function should do one thing well
- **Follow the Azure Functions patterns**: Use the existing routing structure
