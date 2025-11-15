# Implementation: AbuseIPDB

Implementation details for the AbuseIPDB check and report endpoints.

## Overview

The AbuseIPDB integration provides IP reputation checking and abuse reporting capabilities through the AbuseIPDB API v2. The implementation supports both IPv4 and IPv6 addresses with comprehensive error handling and validation.

## Architecture

```
Request → HTTP Trigger → Request Parser → AbuseIPDB Module → API v2 → Response
                                ↓
                         Parameter Validation
```

### Component Flow

1. **HTTP Trigger**: Azure Function receives POST request at `/api/abuseipdb/check` or `/api/abuseipdb/report`
2. **Request Parser**: Extracts parameters from query string or JSON body
3. **Parameter Validation**: Validates required fields (ip, categories, comment)
4. **AbuseIPDB Module**: Calls appropriate function (`check_ip()` or `report_ip()`)
5. **API Request**: Sends authenticated request to AbuseIPDB API v2
6. **Response Handling**: Returns JSON response or error message

## Module: `functions/abuseipdb.py`

### Function: `check_ip(ip: str) -> dict[str, Any]`

Checks the reputation of an IP address using the AbuseIPDB API.

**Parameters:**
- `ip` (str): IPv4 or IPv6 address to check

**Returns:**
- dict[str, Any]: API response containing reputation data

**Raises:**
- `ValueError`: If API key is not configured
- `requests.exceptions.HTTPError`: If API returns error status
- `requests.exceptions.RequestException`: If network error occurs

**Implementation Details:**

```python
def check_ip(ip: str) -> dict[str, Any]:
    """Check an IP's reputation using the AbuseIPDB API."""
    api_key = os.environ.get("ABUSEIPDB_API_KEY")
    if not api_key:
        raise ValueError("ABUSEIPDB_API_KEY environment variable not set")

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": api_key, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": "90"}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise ValueError(f"AbuseIPDB check failed: {exc.response.status_code} {exc.response.text}") from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"AbuseIPDB check failed: {exc}") from exc
```

**Key Features:**
- 10-second timeout prevents hanging on slow connections
- Returns reports from last 90 days (configurable via `maxAgeInDays`)
- Custom error messages include HTTP status codes for debugging
- Exception chaining preserves original error context

### Function: `report_ip(ip: str, categories: str, comment: str) -> dict[str, Any]`

Reports an IP address for abusive behavior.

**Parameters:**
- `ip` (str): IPv4 or IPv6 address to report
- `categories` (str): Comma-separated category IDs (e.g., "15" or "4,14")
- `comment` (str): Detailed description of the abuse (required, max 1024 chars)

**Returns:**
- dict[str, Any]: API response with confirmation

**Raises:**
- `ValueError`: If API key is missing or API returns error
- `requests.exceptions.RequestException`: If network error occurs

**Implementation Details:**

```python
def report_ip(ip: str, categories: str, comment: str) -> dict[str, Any]:
    """Report an IP for abuse to AbuseIPDB."""
    api_key = os.environ.get("ABUSEIPDB_API_KEY")
    if not api_key:
        raise ValueError("ABUSEIPDB_API_KEY environment variable not set")

    url = "https://api.abuseipdb.com/api/v2/report"
    headers = {"Key": api_key, "Accept": "application/json"}
    data = {"ip": ip, "categories": categories, "comment": comment}

    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as exc:
        raise ValueError(f"AbuseIPDB report failed: {exc.response.status_code} {exc.response.text}") from exc
    except requests.exceptions.RequestException as exc:
        raise ValueError(f"AbuseIPDB report failed: {exc}") from exc
```

**Key Features:**
- Accepts comma-separated categories for multiple abuse types
- Comment is required by API (enforced by AbuseIPDB, not function)
- POST request sends data in `application/x-www-form-urlencoded` format
- Returns updated abuse confidence score after report

## HTTP Endpoints: `function_app.py`

### Endpoint: `/api/abuseipdb/check` (POST)

Azure Function HTTP trigger for checking IP reputation.

**Request Format:**
- Method: POST
- Content-Type: application/json (optional)
- Body: `{"ip": "1.2.3.4"}` or query param `?ip=1.2.3.4`

**Implementation:**

```python
@app.route(route="abuseipdb/check", methods=["POST"])
def abuseipdb_check(req: func.HttpRequest) -> func.HttpResponse:
    """Check an IP address against the AbuseIPDB database."""
    logging.info("Processing AbuseIPDB check request")

    # Extract IP from query param or JSON body
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
        result = check_ip(ip)
        return func.HttpResponse(
            json.dumps(result, indent=2), mimetype="application/json", status_code=200
        )
    except Exception as exc:
        logging.error(f"AbuseIPDB check error: {exc}")
        return func.HttpResponse(f"Error: {exc}", status_code=500)
```

**Features:**
- Supports both query parameters and JSON body
- Returns formatted JSON with 2-space indentation
- Logs errors for debugging
- Returns 400 for missing parameters, 500 for API errors

### Endpoint: `/api/abuseipdb/report` (POST)

Azure Function HTTP trigger for reporting IP abuse.

**Request Format:**
- Method: POST
- Content-Type: application/json (optional)
- Body: `{"ip": "1.2.3.4", "categories": "15", "comment": "SSH brute force"}`
- Query params: `?ip=1.2.3.4&categories=15&comment=SSH%20brute%20force`

**Implementation:**

```python
@app.route(route="abuseipdb/report", methods=["POST"])
def abuseipdb_report(req: func.HttpRequest) -> func.HttpResponse:
    """Report an IP address to AbuseIPDB."""
    logging.info("Processing AbuseIPDB report request")

    # Extract parameters from query or JSON body
    ip = req.params.get("ip")
    categories = req.params.get("categories")
    comment = req.params.get("comment")

    if not all([ip, categories, comment]):
        try:
            req_body = req.get_json()
            ip = ip or req_body.get("ip")
            categories = categories or req_body.get("categories")
            comment = comment or req_body.get("comment")
        except ValueError:
            pass

    if not all([ip, categories, comment]):
        return func.HttpResponse(
            "Missing required parameters: ip, categories, comment", status_code=400
        )

    try:
        result = report_ip(ip, categories, comment)
        return func.HttpResponse(
            json.dumps(result, indent=2), mimetype="application/json", status_code=200
        )
    except Exception as exc:
        logging.error(f"AbuseIPDB report error: {exc}")
        return func.HttpResponse(f"Error: {exc}", status_code=500)
```

**Features:**
- Validates all three required parameters
- Supports both query parameters and JSON body
- Graceful error handling for missing parameters
- Logs all reports for audit trail

## Configuration

### Environment Variables

Set these in `local.settings.json` for local development:

```json
{
  "IsEncrypted": false,
  "Values": {
    "ABUSEIPDB_API_KEY": "your-api-key-here",
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

For Azure deployment, configure in Application Settings:
```bash
az functionapp config appsettings set --name <function-app> --resource-group <rg> \
  --settings "ABUSEIPDB_API_KEY=your-api-key-here"
```

### API Key Setup

1. Sign up at https://www.abuseipdb.com/register
2. Navigate to API → Create Key
3. Copy the API key
4. Add to environment configuration

**Free Tier Limits:**
- 1,000 checks per day
- 1,000 reports per day
- 90-day maximum report age

## Error Handling

### Error Response Patterns

**Missing API Key:**
```
Error: ABUSEIPDB_API_KEY environment variable not set
```
Status: 500

**Invalid IP Address:**
```
Error: AbuseIPDB check failed: 422 {"errors":[{"detail":"Invalid IP address","status":422}]}
```
Status: 500

**Rate Limit Exceeded:**
```
Error: AbuseIPDB check failed: 429 Too Many Requests
```
Status: 500

**Invalid Category:**
```
Error: AbuseIPDB report failed: 422 Invalid category
```
Status: 500

**Network Timeout:**
```
Error: AbuseIPDB check failed: HTTPSConnectionPool(host='api.abuseipdb.com', port=443): Read timed out. (read timeout=10)
```
Status: 500

## Testing Strategy

### Unit Tests (`test_abuseipdb.py`)

Mock the `requests` library to test function logic without API calls:

```python
@pytest.mark.mock
def test_check_ip_success(mock_env, mock_requests_get):
    mock_requests_get.return_value = MockResponse(
        {"data": {"ipAddress": "8.8.8.8", "abuseConfidenceScore": 0}}, 200
    )
    result = check_ip("8.8.8.8")
    assert result["data"]["ipAddress"] == "8.8.8.8"
```

### Endpoint Tests (`test_abuseipdb_endpoint.py`)

Test HTTP endpoints with mocked backend:

```python
@pytest.mark.endpoint
def test_check_endpoint_success(mock_check_ip):
    mock_check_ip.return_value = {"data": {"abuseConfidenceScore": 0}}
    response = requests.post("http://localhost:7071/api/abuseipdb/check?ip=8.8.8.8")
    assert response.status_code == 200
```

### Live Tests (`test_abuseipdb_live.py`)

Test against real API (requires API key):

```python
@pytest.mark.live
def test_live_check_google_dns():
    response = requests.post("http://localhost:7071/api/abuseipdb/check?ip=8.8.8.8")
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["ipAddress"] == "8.8.8.8"
```

## Best Practices

### Security

1. **Never expose API key**: Store in environment variables, never commit to source control
2. **Validate input**: Sanitize IP addresses before passing to API
3. **Rate limit protection**: Implement caching to avoid exceeding daily limits
4. **Audit logging**: Log all reports with timestamps for accountability

### Performance

1. **Connection pooling**: Reuse HTTP connections for multiple requests
2. **Caching**: Cache check results for frequently queried IPs (TTL: 1 hour)
3. **Timeout handling**: 10-second timeout prevents indefinite hangs
4. **Batch processing**: Queue multiple reports for batch submission

### Reliability

1. **Error handling**: Catch and log all exceptions with context
2. **Retry logic**: Implement exponential backoff for transient failures
3. **Graceful degradation**: Return cached data if API is unavailable
4. **Health checks**: Monitor API availability and rate limit status

## Common Category IDs

| ID  | Category            | Use Case                              |
|-----|---------------------|---------------------------------------|
| 3   | Fraud Orders        | E-commerce fraud, fake orders         |
| 4   | DDoS Attack         | Distributed denial of service         |
| 9   | Hacking             | System compromise, unauthorized access|
| 10  | Spam                | Generic spam activity                 |
| 14  | Port Scan           | Network reconnaissance                |
| 15  | Brute-Force         | Login attempts, credential stuffing   |
| 18  | Web Spam            | Comment/forum spam                    |
| 19  | Email Spam          | Unsolicited bulk email                |
| 20  | Blog Spam           | Blog comment spam                     |
| 21  | VPN IP              | VPN exit node (informational)         |
| 22  | DNS Compromise      | DNS poisoning, manipulation           |

Full list: https://www.abuseipdb.com/categories

## Integration Examples

### Automated Firewall Rules

```python
def auto_block_malicious_ips():
    """Check IPs from failed login logs and auto-block high-risk ones."""
    for ip in get_failed_login_ips():
        result = check_ip(ip)
        score = result["data"]["abuseConfidenceScore"]
        if score > 75:  # High confidence of abuse
            add_firewall_rule(ip, "block")
            logging.info(f"Blocked {ip} (score: {score})")
```

### Bulk Report Processing

```python
def report_attack_ips(attack_log):
    """Report all IPs involved in a DDoS attack."""
    for entry in attack_log:
        try:
            report_ip(
                ip=entry["ip"],
                categories="4",  # DDoS
                comment=f"DDoS attack at {entry['timestamp']}: {entry['details']}"
            )
        except Exception as exc:
            logging.error(f"Failed to report {entry['ip']}: {exc}")
```

## Troubleshooting

### Issue: "ABUSEIPDB_API_KEY environment variable not set"

**Cause**: API key not configured in environment
**Solution**: Add to `local.settings.json` or Azure Application Settings

### Issue: Rate limit exceeded (429)

**Cause**: Exceeded daily API quota (1,000 requests/day for free tier)
**Solution**: 
- Implement caching to reduce API calls
- Upgrade to paid tier
- Wait for quota reset (midnight UTC)

### Issue: Invalid IP address (422)

**Cause**: Malformed IP address or unsupported format
**Solution**: Validate IP format before calling API (use `ipaddress` module)

### Issue: Connection timeout

**Cause**: Network issues or API downtime
**Solution**: 
- Check internet connectivity
- Verify API status at https://status.abuseipdb.com
- Implement retry logic with exponential backoff

## References

- AbuseIPDB API Documentation: https://docs.abuseipdb.com/
- Category List: https://www.abuseipdb.com/categories
- API Status Page: https://status.abuseipdb.com/
- Rate Limit Details: https://docs.abuseipdb.com/#rate-limit
