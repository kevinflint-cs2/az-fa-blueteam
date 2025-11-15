# Implementation: AlienVault OTX

Implementation details for the AlienVault Open Threat Exchange (OTX) threat intelligence endpoints.

## Overview

The AlienVault OTX integration provides threat intelligence lookups for URLs, IP addresses, file hashes, and domains through the AlienVault OTX API v1. The implementation supports both IPv4 and IPv6 addresses with comprehensive error handling and validation.

## Architecture

```
Request → HTTP Trigger → Request Parser → AlienVault Module → OTX API v1 → Response
                                ↓
                         Parameter Validation
                                ↓
                         IP Address Validation (IP endpoint only)
```

### Component Flow

1. **HTTP Trigger**: Azure Function receives POST request at `/api/alienvault/*`
2. **Request Parser**: Extracts parameters from query string or JSON body
3. **Parameter Validation**: Validates required fields (url, ip, hash, or domain)
4. **IP Validation**: For IP submissions, validates IPv4/IPv6 format using `ipaddress` module
5. **AlienVault Module**: Calls appropriate function (`submit_url()`, `submit_ip()`, `submit_hash()`, or `submit_domain()`)
6. **API Request**: Sends authenticated request to AlienVault OTX API v1
7. **Response Handling**: Returns JSON response with threat intelligence data

## Module: `functions/alienvault.py`

### Helper Function: `get_api_key() -> str`

Retrieves the AlienVault API key from environment variables.

**Returns:**
- str: API key value

**Raises:**
- `ValueError`: If API key is not configured

**Implementation:**

```python
def get_api_key() -> str:
    """Get the AlienVault API key from environment variables."""
    api_key = os.environ.get("ALIENVAULT_API_KEY")
    if not api_key:
        raise ValueError("ALIENVAULT_API_KEY environment variable not set")
    return api_key
```

**Purpose:**
- Centralizes API key retrieval logic
- Provides clear error message if key is missing
- Used by all submission functions

### Function: `submit_url(url: str) -> dict[str, Any]`

Submits a URL to AlienVault OTX for threat intelligence analysis.

**Parameters:**
- `url` (str): The URL to check (full URL including protocol)

**Returns:**
- dict[str, Any]: API response containing threat intelligence data

**Raises:**
- `ValueError`: If API key is missing or API returns error
- `requests.exceptions.RequestException`: If network error occurs

**Implementation:**

```python
def submit_url(url: str) -> dict[str, Any]:
    """Submit a URL to AlienVault OTX for analysis."""
    api_key = get_api_key()
    endpoint = f"https://otx.alienvault.com/api/v1/indicators/url/{url}/general"
    headers = {"X-OTX-API-KEY": api_key}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise ValueError(
            f"AlienVault API request failed: {exc.response.status_code} {exc.response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"AlienVault API request failed: {exc}") from exc
```

**Key Features:**
- URL is embedded directly in API endpoint path
- 10-second timeout prevents hanging
- Returns general threat intelligence data
- Exception chaining preserves error context

**API Endpoint:**
- `GET https://otx.alienvault.com/api/v1/indicators/url/{url}/general`

### Function: `submit_ip(ip: str) -> dict[str, Any]`

Submits an IP address (IPv4 or IPv6) to AlienVault OTX for threat intelligence analysis.

**Parameters:**
- `ip` (str): IPv4 or IPv6 address to check

**Returns:**
- dict[str, Any]: API response with threat intelligence and geolocation data

**Raises:**
- `ValueError`: If IP format is invalid, API key is missing, or API returns error
- `requests.exceptions.RequestException`: If network error occurs

**Implementation:**

```python
def submit_ip(ip: str) -> dict[str, Any]:
    """Submit an IP address to AlienVault OTX for analysis."""
    # Validate IP address format
    try:
        ipaddress.ip_address(ip)
    except ValueError as exc:
        raise ValueError(f"Invalid IP address format: {ip}") from exc

    api_key = get_api_key()
    endpoint = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
    headers = {"X-OTX-API-KEY": api_key}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise ValueError(
            f"AlienVault API request failed: {exc.response.status_code} {exc.response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"AlienVault API request failed: {exc}") from exc
```

**Key Features:**
- Validates IP format using Python's `ipaddress` module (supports both IPv4 and IPv6)
- Pre-validation prevents invalid API calls
- Returns comprehensive threat and geolocation data
- Endpoint path uses "IPv4" but works for IPv6 as well

**API Endpoint:**
- `GET https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general`

### Function: `submit_hash(file_hash: str) -> dict[str, Any]`

Submits a file hash (MD5, SHA1, or SHA256) to AlienVault OTX for malware analysis.

**Parameters:**
- `file_hash` (str): File hash to check (MD5, SHA1, or SHA256)

**Returns:**
- dict[str, Any]: API response with malware analysis data

**Raises:**
- `ValueError`: If API key is missing or API returns error
- `requests.exceptions.RequestException`: If network error occurs

**Implementation:**

```python
def submit_hash(file_hash: str) -> dict[str, Any]:
    """Submit a file hash to AlienVault OTX for analysis."""
    api_key = get_api_key()
    endpoint = f"https://otx.alienvault.com/api/v1/indicators/file/{file_hash}/general"
    headers = {"X-OTX-API-KEY": api_key}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise ValueError(
            f"AlienVault API request failed: {exc.response.status_code} {exc.response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"AlienVault API request failed: {exc}") from exc
```

**Key Features:**
- Accepts any hash type (MD5, SHA1, SHA256)
- No hash validation (API handles format detection)
- Returns malware analysis and detection results
- Useful for file integrity checks and malware identification

**API Endpoint:**
- `GET https://otx.alienvault.com/api/v1/indicators/file/{hash}/general`

### Function: `submit_domain(domain: str) -> dict[str, Any]`

Submits a domain name to AlienVault OTX for threat intelligence analysis.

**Parameters:**
- `domain` (str): Domain name to check (e.g., "example.com")

**Returns:**
- dict[str, Any]: API response with threat intelligence data

**Raises:**
- `ValueError`: If API key is missing or API returns error
- `requests.exceptions.RequestException`: If network error occurs

**Implementation:**

```python
def submit_domain(domain: str) -> dict[str, Any]:
    """Submit a domain to AlienVault OTX for analysis."""
    api_key = get_api_key()
    endpoint = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/general"
    headers = {"X-OTX-API-KEY": api_key}

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise ValueError(
            f"AlienVault API request failed: {exc.response.status_code} {exc.response.text}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"AlienVault API request failed: {exc}") from exc
```

**Key Features:**
- No domain format validation (API handles validation)
- Returns threat intelligence and WHOIS data
- Supports subdomains and TLDs
- Useful for DNS-based threat detection

**API Endpoint:**
- `GET https://otx.alienvault.com/api/v1/indicators/domain/{domain}/general`

## HTTP Endpoints: `function_app.py`

All four endpoints follow the same pattern with different parameter names.

### Endpoint: `/api/alienvault/url` (POST)

Azure Function HTTP trigger for URL threat intelligence lookups.

**Request Format:**
- Method: POST
- Content-Type: application/json (optional)
- Body: `{"url": "https://example.com"}` or query param `?url=https://example.com`

**Implementation:**

```python
@app.route(route="alienvault/url", methods=["POST"])
def alienvault_url(req: func.HttpRequest) -> func.HttpResponse:
    """Submit a URL to AlienVault OTX for threat intelligence."""
    logging.info("Processing AlienVault URL submission")

    url = req.params.get("url")
    if not url:
        try:
            req_body = req.get_json()
            url = req_body.get("url")
        except ValueError:
            pass

    if not url:
        return func.HttpResponse("Missing required parameter: url", status_code=400)

    try:
        result = submit_url(url)
        return func.HttpResponse(
            json.dumps(result, indent=2), mimetype="application/json", status_code=200
        )
    except Exception as exc:
        logging.error(f"AlienVault URL submission error: {exc}")
        return func.HttpResponse(f"Error: {exc}", status_code=500)
```

### Endpoint: `/api/alienvault/ip` (POST)

Azure Function HTTP trigger for IP address threat intelligence lookups.

**Request Format:**
- Method: POST
- Content-Type: application/json (optional)
- Body: `{"ip": "8.8.8.8"}` or query param `?ip=8.8.8.8`

**Implementation:**

```python
@app.route(route="alienvault/ip", methods=["POST"])
def alienvault_ip(req: func.HttpRequest) -> func.HttpResponse:
    """Submit an IP address to AlienVault OTX for threat intelligence."""
    logging.info("Processing AlienVault IP submission")

    ip = req.params.get("ip")
    if not ip:
        try:
            req_body = req.get_json()
            ip = req_body.get("ip")
        except ValueError:
            pass

    if not ip:
        return func.HttpResponse("Missing required parameter: ip", status_code=400)

    try:
        result = submit_ip(ip)
        return func.HttpResponse(
            json.dumps(result, indent=2), mimetype="application/json", status_code=200
        )
    except Exception as exc:
        logging.error(f"AlienVault IP submission error: {exc}")
        return func.HttpResponse(f"Error: {exc}", status_code=500)
```

### Endpoint: `/api/alienvault/hash` (POST)

Azure Function HTTP trigger for file hash malware lookups.

**Request Format:**
- Method: POST
- Content-Type: application/json (optional)
- Body: `{"hash": "d41d8cd98f00b204e9800998ecf8427e"}` or query param `?hash=...`

**Implementation:**

```python
@app.route(route="alienvault/hash", methods=["POST"])
def alienvault_hash(req: func.HttpRequest) -> func.HttpResponse:
    """Submit a file hash to AlienVault OTX for threat intelligence."""
    logging.info("Processing AlienVault hash submission")

    file_hash = req.params.get("hash")
    if not file_hash:
        try:
            req_body = req.get_json()
            file_hash = req_body.get("hash")
        except ValueError:
            pass

    if not file_hash:
        return func.HttpResponse("Missing required parameter: hash", status_code=400)

    try:
        result = submit_hash(file_hash)
        return func.HttpResponse(
            json.dumps(result, indent=2), mimetype="application/json", status_code=200
        )
    except Exception as exc:
        logging.error(f"AlienVault hash submission error: {exc}")
        return func.HttpResponse(f"Error: {exc}", status_code=500)
```

### Endpoint: `/api/alienvault/domain` (POST)

Azure Function HTTP trigger for domain threat intelligence lookups.

**Request Format:**
- Method: POST
- Content-Type: application/json (optional)
- Body: `{"domain": "example.com"}` or query param `?domain=example.com`

**Implementation:**

```python
@app.route(route="alienvault/domain", methods=["POST"])
def alienvault_domain(req: func.HttpRequest) -> func.HttpResponse:
    """Submit a domain to AlienVault OTX for threat intelligence."""
    logging.info("Processing AlienVault domain submission")

    domain = req.params.get("domain")
    if not domain:
        try:
            req_body = req.get_json()
            domain = req_body.get("domain")
        except ValueError:
            pass

    if not domain:
        return func.HttpResponse("Missing required parameter: domain", status_code=400)

    try:
        result = submit_domain(domain)
        return func.HttpResponse(
            json.dumps(result, indent=2), mimetype="application/json", status_code=200
        )
    except Exception as exc:
        logging.error(f"AlienVault domain submission error: {exc}")
        return func.HttpResponse(f"Error: {exc}", status_code=500)
```

**Common Features (All Endpoints):**
- Supports both query parameters and JSON body
- Returns formatted JSON with 2-space indentation
- Logs errors for debugging
- Returns 400 for missing parameters, 500 for API/network errors

## Configuration

### Environment Variables

Set these in `local.settings.json` for local development:

```json
{
  "IsEncrypted": false,
  "Values": {
    "ALIENVAULT_API_KEY": "your-api-key-here",
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

For Azure deployment, configure in Application Settings:
```bash
az functionapp config appsettings set --name <function-app> --resource-group <rg> \
  --settings "ALIENVAULT_API_KEY=your-api-key-here"
```

### API Key Setup

1. Create a free account at https://otx.alienvault.com/
2. Navigate to Settings → API Integration
3. Copy your OTX API key
4. Add to environment configuration

**Free Tier Limits:**
- 10 requests per second
- No daily request limit
- Unlimited pulse subscriptions
- Full API access

## Error Handling

### Error Response Patterns

**Missing API Key:**
```
Error: ALIENVAULT_API_KEY environment variable not set
```
Status: 500

**Invalid IP Address:**
```
Error: Invalid IP address format: 999.999.999.999
```
Status: 500

**Missing Parameter:**
```
Missing required parameter: url
```
Status: 400

**API Error (404 Not Found):**
```
Error: AlienVault API request failed: 404 {"detail":"Not found."}
```
Status: 500

**Rate Limit Exceeded:**
```
Error: AlienVault API request failed: 429 Too Many Requests
```
Status: 500

**Network Timeout:**
```
Error: AlienVault API request failed: HTTPSConnectionPool(host='otx.alienvault.com', port=443): Read timed out. (read timeout=10)
```
Status: 500

## Testing Strategy

### Unit Tests (`test_alienvault.py`)

Mock the `requests` library to test function logic without API calls:

```python
@pytest.mark.mock
def test_submit_url_success(mock_env, mock_requests_get):
    mock_requests_get.return_value = MockResponse(
        {"indicator": "https://example.com", "pulse_info": {"count": 0}}, 200
    )
    result = submit_url("https://example.com")
    assert result["indicator"] == "https://example.com"
```

### Endpoint Tests (`test_alienvault_endpoint.py`)

Test HTTP endpoints with mocked backend:

```python
@pytest.mark.endpoint
def test_url_endpoint_success(mock_submit_url):
    mock_submit_url.return_value = {"pulse_info": {"count": 0}}
    response = requests.post("http://localhost:7071/api/alienvault/url?url=https://example.com")
    assert response.status_code == 200
```

### Live Tests (`test_alienvault_live.py`)

Test against real API (requires API key):

```python
@pytest.mark.live
def test_live_url_google():
    response = requests.post("http://localhost:7071/api/alienvault/url?url=https://google.com")
    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "https://google.com"
```

## Best Practices

### Security

1. **Never expose API key**: Store in environment variables, never commit to source control
2. **Validate input**: Use `ipaddress` module for IP validation before API calls
3. **Rate limit protection**: Implement request throttling (10 req/sec limit)
4. **Audit logging**: Log all submissions with timestamps for security monitoring

### Performance

1. **Connection pooling**: Reuse HTTP connections for multiple requests
2. **Caching**: Cache results for frequently queried indicators (TTL: 1 hour)
3. **Timeout handling**: 10-second timeout prevents indefinite hangs
4. **Parallel requests**: Query multiple indicators concurrently (respect rate limit)

### Reliability

1. **Error handling**: Catch and log all exceptions with full context
2. **Retry logic**: Implement exponential backoff for transient failures
3. **Graceful degradation**: Return cached data if API is unavailable
4. **Health checks**: Monitor API availability and rate limit status

### Data Interpretation

1. **Pulse count**: Higher count indicates more threat reports (>5 is concerning)
2. **Reputation score**: For IPs, 7+ indicates high risk
3. **False positives**: Check `false_positive` field before taking action
4. **Multiple sources**: Combine with AbuseIPDB and other threat feeds for validation

## Common Use Cases

### Phishing Detection

```python
def check_suspicious_url(url):
    """Check URL from email/SMS for phishing indicators."""
    result = submit_url(url)
    pulse_count = result["pulse_info"]["count"]
    
    if pulse_count > 0:
        logging.warning(f"Phishing URL detected: {url} (pulses: {pulse_count})")
        return True
    return False
```

### Malware Analysis

```python
def analyze_file_hash(file_hash):
    """Check file hash for known malware."""
    result = submit_hash(file_hash)
    
    if result.get("malware"):
        detections = result["malware"].get("detections", {})
        logging.error(f"Malware detected: {detections}")
        return True
    return False
```

### C2 Detection

```python
def detect_c2_domain(domain):
    """Check domain for command & control infrastructure."""
    result = submit_domain(domain)
    pulse_count = result["pulse_info"]["count"]
    
    # Check for C2-related tags
    for pulse in result["pulse_info"]["pulses"]:
        tags = pulse.get("tags", [])
        if any(tag in tags for tag in ["c2", "command-control", "botnet"]):
            logging.critical(f"C2 domain detected: {domain}")
            return True
    
    return pulse_count > 10  # High pulse count also indicates C2
```

### IP Reputation Check

```python
def block_malicious_ip(ip):
    """Check IP reputation and block if malicious."""
    result = submit_ip(ip)
    reputation = result.get("reputation", 0)
    pulse_count = result["pulse_info"]["count"]
    
    if reputation >= 7 or pulse_count > 10:
        logging.info(f"Blocking malicious IP: {ip} (rep: {reputation}, pulses: {pulse_count})")
        return True
    return False
```

## Integration Examples

### SIEM Enrichment

```python
def enrich_security_event(event):
    """Enrich SIEM event with threat intelligence."""
    enriched = event.copy()
    
    if "source_ip" in event:
        ip_intel = submit_ip(event["source_ip"])
        enriched["threat_score"] = ip_intel.get("reputation", 0)
        enriched["pulse_count"] = ip_intel["pulse_info"]["count"]
        enriched["country"] = ip_intel.get("country_name")
    
    if "url" in event:
        url_intel = submit_url(event["url"])
        enriched["url_threat_pulses"] = url_intel["pulse_info"]["count"]
    
    return enriched
```

### Automated Threat Response

```python
def auto_respond_to_threat(indicator, indicator_type):
    """Automatically respond to detected threats."""
    if indicator_type == "ip":
        result = submit_ip(indicator)
    elif indicator_type == "domain":
        result = submit_domain(indicator)
    elif indicator_type == "url":
        result = submit_url(indicator)
    else:
        return
    
    pulse_count = result["pulse_info"]["count"]
    
    if pulse_count > 20:
        # High-confidence threat - auto-block
        add_to_blacklist(indicator)
        send_alert(f"Auto-blocked threat: {indicator} (pulses: {pulse_count})")
    elif pulse_count > 5:
        # Medium-confidence - alert for review
        send_alert(f"Potential threat detected: {indicator} (pulses: {pulse_count})")
```

## Troubleshooting

### Issue: "ALIENVAULT_API_KEY environment variable not set"

**Cause**: API key not configured in environment  
**Solution**: Add to `local.settings.json` or Azure Application Settings

### Issue: Rate limit exceeded (429)

**Cause**: Exceeded 10 requests per second  
**Solution**: 
- Implement request throttling
- Use connection pooling with rate limiting
- Add delays between batch requests

### Issue: Invalid IP address format

**Cause**: Malformed IP address or unsupported format  
**Solution**: Validate IP format using `ipaddress.ip_address()` before submission

### Issue: No pulse information (count = 0)

**Cause**: Indicator not in OTX database or genuinely clean  
**Solution**: 
- Check other threat intelligence sources
- Submit to OTX community if confirmed malicious
- Monitor for future reports

### Issue: Connection timeout

**Cause**: Network issues or API downtime  
**Solution**: 
- Check internet connectivity
- Verify API status at https://otx.alienvault.com/
- Implement retry logic with exponential backoff

## References

- AlienVault OTX Portal: https://otx.alienvault.com/
- API Documentation: https://otx.alienvault.com/api
- Pulse Explorer: https://otx.alienvault.com/browse/pulses
- Community Forum: https://otx.alienvault.com/forums
- API Python SDK: https://github.com/AlienVault-OTX/OTX-Python-SDK
- OTX API v1 Endpoints: https://otx.alienvault.com/assets/static/external_api.html
