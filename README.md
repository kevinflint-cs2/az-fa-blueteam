# az-fa-blueteam

Lightweight Azure Function App (Python) that provides on-demand blue-team enrichment endpoints — AbuseIPDB, URL reputation (Web of Trust), VirusTotal, and other public-API lookups — to accelerate triage, hunting, and automation.

## Features
- **Helloworld Endpoint**: Returns a greeting for the provided name.
- **Goodbye Endpoint**: Returns a farewell for the provided name.
- Easily extensible for additional enrichment APIs (e.g., AbuseIPDB, VirusTotal, Web of Trust).

## Project Structure
```
functions/           # Business logic for each endpoint
  helloworld.py      # Logic for the helloworld endpoint
  goodbye.py         # Logic for the goodbye endpoint
function_app.py      # Azure Functions HTTP triggers and routing
requirements.txt     # Python dependencies
requirements-dev.txt # Dev/test dependencies (pytest, requests, etc.)
local.settings.json  # Local Azure Functions settings
host.json            # Azure Functions host configuration
```

## Endpoints
- `GET /api/helloworld?name=YourName` → `Hello, YourName`
- `GET /api/goodbye?name=YourName` → `Goodbye, YourName`

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

### 3. Deployment

You can deploy using the Visual Studio Code Azure extension:
1. Press `Ctrl+Shift+P` in VS Code.
2. Select `Azure Functions: Deploy to Function App`.
3. Follow the prompts to deploy your app.

---

## Extending the App
- Add new logic modules to the `functions/` folder.
- Import and use them in `function_app.py` with a new route.
- Add tests in the `tests/` directory.

## Requirements
- Python 3.8+
- Azure Functions Core Tools
- Visual Studio Code (recommended)
- Azure CLI (for resource management)

## License
MIT
