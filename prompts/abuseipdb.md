I want to create a new endpoint named abuseipdb. And need to draft a plan. 

- Follow the current coding structure and store the file in functions as abuseipdb.py
- In function_app.py import the function/s and create a new route/s
- Read in this page, https://docs.abuseipdb.com/#check-endpoint, as I want to submit an ip to check 
- Read in this page, https://docs.abuseipdb.com/#report-endpoint, as I want to submit an ip to report
- I am thinking both will need a parameter ip, but we could add a parameter type and it could be check or report
    - Identify a different strategies for this and provide a recommendation 
- Tests will need to be written to test both calls
- The README.md will need to be update

Draft a plan of action, provide suggestions and recommendations. 


Add these to the plan

Security: Store the AbuseIPDB API key in an environment variable
Error Handling: Return clear error messages for missing/invalid parameters and failed API calls.
Extensibility: Structure the code so adding more AbuseIPDB endpoints or other enrichment APIs is easy.
Testing: Use mocking for HTTP requests in tests to avoid hitting the real AbuseIPDB API.

I want to proceed with the plan, but one last set of additions is to ensure doc strings are created, ruff check can run with no errors, and  mypy will run with no errors. 

Final Plan for AbuseIPDB Endpoints

# Create functions/abuseipdb.py
- Implement two functions: one for the AbuseIPDB "check" endpoint and one for the "report" endpoint.
- Each function must have a clear, complete docstring.
- Type annotations must be present for all functions and parameters.
- Code must pass ruff (linting) and mypy (type checking) with no errors.
- Read the AbuseIPDB API key from an environment variable.

## Update function_app.py
- Import the new functions from functions/abuseipdb.py.
- Add new routes: /api/abuseipdb/check and /api/abuseipdb/report.
- Extract and validate parameters for each route.
- Return clear error messages for missing/invalid parameters and failed API calls.
- Ensure all new/modified code passes ruff and mypy.

## Testing
- Add tests in tests/test_abuseipdb.py for both endpoints.
- Use mocking for HTTP requests to AbuseIPDB.
- Ensure tests pass, and code is type-safe and lint-free.

## Extensibility
- Structure code for easy addition of new endpoints.
- Use clear patterns for parameter extraction, error handling, and API calls.
- Document how to extend in the README.

## Update README.md
- Document new endpoints, parameters, and example usage.
- Note the need to set the AbuseIPDB API key as an environment variable.
- Add notes on error handling, extensibility, and testing.
- Document how to run ruff and mypy checks.

## All code and tests must:
- Have proper docstrings.
- Pass ruff (lint) and mypy (type check) with no errors.

