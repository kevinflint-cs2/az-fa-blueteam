# az-fa-blueteam

Lightweight Azure Function App (Python) that provides on-demand blue-team enrichment endpoints — AbuseIPDB, URL reputation (Web of Trust), VirusTotal, and other public-API lookups — to accelerate triage, hunting, and automation.

## Features
- **Helloworld Endpoint**: Returns a greeting for the provided name.
- **Goodbye Endpoint**: Returns a farewell for the provided name.
- **AbuseIPDB Endpoints**: Check and report IPs using the AbuseIPDB API.
- Easily extensible for additional enrichment APIs (e.g., AbuseIPDB, VirusTotal, Web of Trust).

## Project Structure
```
functions/           # Business logic for each endpoint
  helloworld.py      # Logic for the helloworld endpoint
  goodbye.py         # Logic for the goodbye endpoint
  abuseipdb.py       # Logic for AbuseIPDB check/report endpoints
function_app.py      # Azure Functions HTTP triggers and routing
requirements.txt     # Python dependencies
requirements-dev.txt # Dev/test dependencies (pytest, requests, etc.)
local.settings.json  # Local Azure Functions settings
host.json            # Azure Functions host configuration
```

## Endpoints
- `GET /api/helloworld?name=YourName` → `Hello, YourName`
- `GET /api/goodbye?name=YourName` → `Goodbye, YourName`
- `GET /api/abuseipdb/check?ip=1.2.3.4` → AbuseIPDB check for an IP (returns JSON)
- `POST /api/abuseipdb/report` with JSON body `{ "ip": "1.2.3.4", "categories": "18", "comment": "test" }` → AbuseIPDB report (returns JSON)

## Usage

### 1. Setup

#### Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Install development/test dependencies (for running tests)
```bash
pip install -r requirements-dev.txt
```

### 2. Local Development

#### Start the Azure Functions host
```bash
func start
```

#### Run automated tests
```bash
pytest ./tests -vv
```

#### Run static analysis
```bash
ruff check .
mypy .
```

### 3. Deployment

You can deploy using the Visual Studio Code Azure extension:
1. Press `Ctrl+Shift+P` in VS Code.
2. Select `Azure Functions: Deploy to Function App`.
3. Follow the prompts to deploy your app.

---

## AbuseIPDB API Key Security
- The AbuseIPDB API key must be set as an environment variable: `ABUSEIPDB_API_KEY`.
- For local development, add it to your `local.settings.json` under `Values` (do not commit this file).
- For production, set it as an Application Setting in the Azure portal.

## Error Handling
- All endpoints return clear error messages for missing/invalid parameters and failed API calls.
- HTTP 400 for missing/invalid input, HTTP 500 for API or internal errors.

## Extending the App
- Add new logic modules to the `functions/` folder.
- Import and use them in `function_app.py` with a new route.
- Add tests in the `tests/` directory.
- Follow the same structure for docstrings, type annotations, and error handling.

## Requirements
- Python 3.8+
- Azure Functions Core Tools
- Visual Studio Code (recommended)
- Azure CLI (for resource management)
- [ruff](https://docs.astral.sh/ruff/) for linting
- [mypy](http://mypy-lang.org/) for type checking

## License
MIT
