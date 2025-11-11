# az-fa-blueteam

Lightweight Azure Function App (Python) that provides on-demand blue-team enrichment endpoints — AbuseIPDB, URL reputation (Web of Trust), VirusTotal, and other public-API lookups — to accelerate triage, hunting, and automation.

## Features
- **AbuseIPDB Endpoints**: Check and report IPs using the AbuseIPDB API.
- Easily extensible for additional enrichment APIs (e.g., AbuseIPDB, VirusTotal, Web of Trust).
- **DNS resolver endpoint**: Resolve domain names (A/AAAA/NS) with basic DNSSEC presence detection and return structured results including IPs, nameservers, dnssec status, metrics, and trace info.
- Easily extensible for additional enrichment APIs (e.g., AbuseIPDB, VirusTotal, Web of Trust).

## Project Structure
```
functions/           # Business logic for each endpoint
  abuseipdb.py       # Logic for AbuseIPDB check/report endpoints
  alienvault.py      # Logic for AlienVault endpoints
  dns_resolver.py    # Async DNS resolver with caching, retries, and DNSSEC presence checks
function_app.py      # Azure Functions HTTP triggers and routing
requirements.txt     # Python dependencies
requirements-dev.txt # Dev/test dependencies (pytest, requests, etc.)
local.settings.json  # Local Azure Functions settings
host.json            # Azure Functions host configuration
deploy_staging.sh    # Script to create a clean deployment zip
az_fa_blueteam.zip   # Deployment zip (created by script, not in repo)
```
## Deployment: Zip for Azure Functions

To create a clean deployment zip (excluding local.settings.json and dev/test files), run:

```bash
./deploy_staging.sh
```

This will create `az_fa_blueteam.zip` in the project root, ready for Azure zip deploy. The script ensures only production files are included.


## Endpoints

- `GET /api/abuseipdb/check?ip=1.2.3.4` → AbuseIPDB check for an IP (returns JSON)
- `POST /api/abuseipdb/report` with JSON body `{ "ip": "1.2.3.4", "categories": "18", "comment": "test" }` → AbuseIPDB report (returns JSON)
- `POST /api/dns/resolve` with JSON body `{ "domains": ["example.com", "google.com"] }` or query param `?domains=example.com,google.com` → Resolve domains and return structured DNS results (A/AAAA/NS, dnssec presence, metrics)
 - `GET /api/whois?q=<query>` or `POST /api/whois` with JSON `{ "q": "<domain|ip>", ... }` → Combined WHOIS/RDAP lookup for domains and IPs (returns normalized JSON)

### AlienVault Endpoints
- `POST /api/alienvault/submit_url` with JSON `{ "url": "http://example.com" }` or query param `?url=...` → Submits a URL for OTX analysis
- `GET /api/alienvault/submit_ip?ip=1.2.3.4` or JSON `{ "ip": "1.2.3.4" }` → OTX info for an IP (IPv4/IPv6)
- `GET /api/alienvault/submit_hash?file_hash=abcd1234` or JSON `{ "file_hash": "abcd1234" }` → OTX info for a file hash
- `GET /api/alienvault/submit_domain?domain=example.com` or JSON `{ "domain": "example.com" }` → OTX info for a domain

All endpoints return JSON. Errors return HTTP 400 for missing/invalid input, HTTP 500 for API/internal errors.

#### Example Usage
```bash
# Submit a URL
curl -X POST "http://localhost:7071/api/alienvault/submit_url" -H "Content-Type: application/json" -d '{"url": "http://example.com"}'
# Query an IP
curl "http://localhost:7071/api/alienvault/submit_ip?ip=1.2.3.4"
# Query a file hash
curl "http://localhost:7071/api/alienvault/submit_hash?file_hash=abcd1234"
# Query a domain
curl "http://localhost:7071/api/alienvault/submit_domain?domain=example.com"
# AbuseIPDB: check an IP
curl "http://localhost:7071/api/abuseipdb/check?ip=1.2.3.4"
# DNS resolver: resolve domains
curl -X POST "http://localhost:7071/api/dns/resolve" -H "Content-Type: application/json" -d '{"domains": ["example.com"]}'

# Whois examples
curl "http://localhost:7071/api/whois?q=example.com"
curl -X POST "http://localhost:7071/api/whois" -H "Content-Type: application/json" -d '{ "q": "8.8.8.8", "source": "rdap" }'
```

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

#### Add environment variables (local)

To add the required API keys to your local Azure Functions settings (writes to `local.settings.json`), use the Functions Core Tools `func settings add` command. This avoids manual editing and ensures values are placed under the `Values` object.

```bash
# AbuseIPDB API key
func settings add ABUSEIPDB_API_KEY "your_abuseipdb_api_key_here"

# AlienVault API key
func settings add ALIENVAULT_API_KEY "your_alienvault_api_key_here"
```

Notes:
- `local.settings.json` is already listed in `.gitignore` in this repo, so these files should not be committed.
- If you prefer not to write secrets to a file, export them into your shell instead before starting the Functions host (example below).

#### Start the Azure Functions host (local)

Start the Functions host after adding settings and installing dependencies:

```bash
func start
```

### 2. Local Development

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

## API Key Security (AbuseIPDB & AlienVault)
- The AbuseIPDB API key must be set as an environment variable: `ABUSEIPDB_API_KEY`.
- The AlienVault API key must be set as an environment variable: `ALIENVAULT_API_KEY`.
- For local development, add both to your `local.settings.json` under `Values` (do not commit this file).
- For production, set them as Application Settings in the Azure portal.

## Error Handling
- All endpoints return clear error messages for missing/invalid parameters and failed API calls.
- HTTP 400 for missing/invalid input, HTTP 500 for API or internal errors.
- AlienVault endpoints raise errors for missing API key, invalid input, or failed OTX API calls.

## Extending the App
- Add new logic modules to the `functions/` folder (see `alienvault.py` for example: docstrings, type annotations, error handling).
- Import and use them in `function_app.py` with a new route.
- Add tests in the `tests/` directory, using pytest and unittest.mock for HTTP calls.
- Ensure ruff and mypy compliance for all new code.

## Requirements
- Python 3.8+
- Azure Functions Core Tools
- Visual Studio Code (recommended)
- Azure CLI (for resource management)
- [ruff](https://docs.astral.sh/ruff/) for linting
- [mypy](http://mypy-lang.org/) for type checking
- [pytest](https://docs.pytest.org/) for testing


## Linting, Type Checking, and Testing

### Running Tests
- Run only mock (unit) tests:
  ```bash
  pytest -m mock
  # or, to be explicit:
  pytest -k "test_ and not test_alienvault_live"
  ```
- Run only live tests:
  ```bash
  pytest -m live
  ```
- Run all tests:
  ```bash
  pytest ./tests -vv
  ```

Run these before committing or deploying:
```bash
ruff check .
mypy .
pytest ./tests -vv
```

## License
MIT
