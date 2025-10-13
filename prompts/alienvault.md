Plan for AlienValut Endpoints

## Create functions/alienvault.py

- Implement functions: 
    - submit_url which makes a rest api call to /api/v1/indicators/submit_url
    - submit_ip which makes a rest api call to
      - For IPv4 IPs then /api/v1/indicators/IPv4/{ip}/general
      - For IPv6 IPs then /api/v1/indicators/IPv6/{ip}/general
    - submit_hash which makes a rest api call to /api/v1/indicators/file/{file_hash}/general
    - submit_domain which makes a rest api call to /api/v1/indicators/domain/{domain}/general
- Root domain for above rest api calls is https://otx.alienvault.com
- Documentation is located here: https://otx.alienvault.com/api, read documentation for context
- Each function must have a clear, complete docstring.
- Type annotations must be present for all functions and parameters.
- Code must pass ruff (linting) and mypy (type checking) with no errors.
- Create the json needed to use local.settings.json to get the the AlienVault API key.

## Update function_app.py
- Import the new functions from functions/alienvault.py.
- Add new routes:
  - /api/alienvault/submit_url
  - /api/alienvault/submit_ip
  - /api/alienvault/submit_hash
  - /api/alienvault/submit_domain     
- Extract and validate parameters for each route.
- Return clear error messages for missing/invalid parameters and failed API calls.
- Ensure all new/modified code passes ruff and mypy.

## Testing
- Add tests in tests/test_alienvault.py for both endpoints.
- Use mocking for HTTP requests to AlienVault.
- Ensure tests pass, and code is type-safe and lint-free.

## Extensibility
- Structure code for easy addition of new endpoints.
- Use clear patterns for parameter extraction, error handling, and API calls.
- Document how to extend in the README.

## Update README.md
- Document new endpoints, parameters, and example usage.
- Note the need to set the AlienVault API key in local.settings.json. (Also, make the change for the AbuseIPDB API key to use local.settings.json intead of env file)
- Add notes on error handling, extensibility, and testing.
- Document how to run ruff and mypy checks.

## All code and tests must:
- Have proper docstrings.
- Pass ruff (lint) and mypy (type check) with no errors.