# URLScan.io Integration Implementation

## Overview

This document describes the comprehensive implementation of URLScan.io integration for the Azure Functions BlueTeam enrichment application, including URL submission, result retrieval, and search functionality.

## Implementation Option Selected

**Option A: Extended Module with Submit, Result, and Search Functions**

This option was selected because it:
- Maintains consistency with existing repository patterns
- Keeps all URLScan.io functionality in one cohesive module
- Follows the established functional programming approach
- Minimizes code duplication for API key handling and error management
- Provides complete URLScan.io API coverage in a single module

## Architecture

### Module Structure

**File:** `functions/urlscan.py`

**Core Functions:**

1. `submit_url(url: str, visibility: str = "public") -> dict[str, Any]`
   - Core business logic for submitting URLs to URLScan.io
   - Validates parameters and makes API request
   - Returns parsed API response

2. `get_result(uuid: str) -> dict[str, Any]`
   - Retrieves scan results by UUID
   - Handles polling scenarios (404 = not ready)
   - Returns full scan result data

3. `search_scans(query: str, size: int = 100, search_after: str = None) -> dict[str, Any]`
   - Searches for scans using ElasticSearch syntax
   - Supports pagination via search_after
   - Returns search results with metadata

**Entry Point Functions:**

- `handle_request(payload: dict[str, Any]) -> dict[str, Any]`
  - Entry point for submission endpoint
  - Validates payload structure
  - Delegates to `submit_url`
  
- `handle_result_request(payload: dict[str, Any]) -> dict[str, Any]`
  - Entry point for result retrieval endpoint
  - Validates UUID parameter
  - Delegates to `get_result`

- `handle_search_request(payload: dict[str, Any]) -> dict[str, Any]`
  - Entry point for search endpoint
  - Validates query parameters
  - Delegates to `search_scans`

All entry points return standardized response format with `status` and `result` keys.

### HTTP Endpoints

#### 1. `/api/urlscan/submit`
**Method:** POST/GET  
**Auth Level:** FUNCTION

**Request Parameters:**
- `url` (required): The URL to scan
- `visibility` (optional): "public", "unlisted", or "private" (default: "public")

Parameters can be provided via:
- Query string: `?url=https://example.com&visibility=public`
- JSON body: `{"url": "https://example.com", "visibility": "public"}`

**Response Format:**

Success (HTTP 200):
```json
{
  "status": "ok",
  "result": {
    "uuid": "abc123-def456-...",
    "message": "Submission successful",
    "url": "https://urlscan.io/result/abc123-def456-.../",
    "api": "https://urlscan.io/api/v1/result/abc123-def456-.../"
  }
}
```

#### 2. `/api/urlscan/result`
**Method:** GET  
**Auth Level:** FUNCTION

**Request Parameters:**
- `uuid` (required): The scan UUID from submission response

Parameters can be provided via:
- Query string: `?uuid=abc123-def456-...`
- JSON body: `{"uuid": "abc123-def456-..."}`

**Response Format:**

Success (HTTP 200):
```json
{
  "status": "ok",
  "result": {
    "page": {
      "url": "https://example.com",
      "domain": "example.com",
      "ip": "93.184.216.34"
    },
    "lists": {
      "ips": ["93.184.216.34"],
      "domains": ["example.com"]
    },
    "verdicts": {
      "overall": {
        "score": 0,
        "malicious": false
      }
    }
  }
}
```

Not Ready (HTTP 404):
```json
{
  "status": "error",
  "error": {
    "msg": "Scan not ready or not found. Please wait and try again."
  }
}
```

#### 3. `/api/urlscan/search`
**Method:** GET  
**Auth Level:** FUNCTION

**Request Parameters:**
- `q` (required): Search query (ElasticSearch syntax)
- `size` (optional): Number of results (default: 100, max: 10000)
- `search_after` (optional): Pagination cursor from previous result

Parameters can be provided via:
- Query string: `?q=domain:example.com&size=10`
- JSON body: `{"q": "domain:example.com", "size": 10}`

**Response Format:**

Success (HTTP 200):
```json
{
  "status": "ok",
  "result": {
    "results": [
      {
        "_id": "abc123-def456-...",
        "page": {
          "url": "https://example.com",
          "domain": "example.com"
        },
        "task": {
          "visibility": "public",
          "time": "2025-11-15T12:34:56.789Z"
        }
      }
    ],
    "total": 1,
    "has_more": false
  }
}
```

#### Common Error Response

Error (HTTP 400/404/500):
```json
{
  "status": "error",
  "error": {
    "msg": "Error description"
  }
}
```

## API Integration

### URLScan.io API Details

#### Submission API
**Endpoint:** `POST https://urlscan.io/api/v1/scan/`

**Headers:**
- `API-Key: <URLSCAN_API_KEY>`
- `Content-Type: application/json`

**Request Body:**
```json
{
  "url": "https://example.com",
  "visibility": "public"
}
```

**Response:**
```json
{
  "message": "Submission successful",
  "uuid": "abc123-def456-...",
  "result": "https://urlscan.io/result/abc123-def456-.../",
  "api": "https://urlscan.io/api/v1/result/abc123-def456-.../"
}
```

#### Result API
**Endpoint:** `GET https://urlscan.io/api/v1/result/{uuid}/`

**Headers:**
- `API-Key: <URLSCAN_API_KEY>` (optional but recommended)

**Response:** Full scan result JSON with page metadata, lists, statistics, and verdicts

**Note:** Returns 404 while scan is in progress. Recommended polling:
1. Wait 10-30 seconds after submission
2. Poll every 5 seconds until success or timeout

#### Search API
**Endpoint:** `GET https://urlscan.io/api/v1/search/?q={query}&size={size}`

**Headers:**
- `API-Key: <URLSCAN_API_KEY>` (required for private/unlisted scans)

**Query Parameters:**
- `q`: Search query (ElasticSearch syntax)
- `size`: Number of results (default: 100, max: 10000)
- `search_after`: Pagination cursor (comma-separated sort values)

**Response:** Array of scan summaries with pagination metadata

### Error Handling

**Client Errors (HTTP 400):**
- Missing required parameters (`url`, `uuid`, `q`)
- Invalid `visibility` value (not "public", "unlisted", or "private")
- Invalid `size` parameter (< 1 or > 10000)
- Invalid UUID format

**Not Found (HTTP 404):**
- Scan not ready yet (for result endpoint)
- Scan UUID doesn't exist

**Gone (HTTP 410):**
- Scan has been deleted

**Rate Limiting (HTTP 429):**
- URLScan.io API rate limit exceeded
- Client should wait and retry with exponential backoff

**Server Errors (HTTP 500):**
- Missing `URLSCAN_API_KEY` environment variable
- URLScan.io API authentication errors (401)
- Network timeouts
- Unexpected API responses

## Configuration

### Environment Variables

**Required:**
- `URLSCAN_API_KEY`: API key from URLScan.io account

**Optional:**
- `URLSCAN_TIMEOUT`: Request timeout in seconds (default: 10)

### Local Development Setup

Add secret API key using func settings:
```bash
func settings add URLSCAN_API_KEY "your-api-key-here"
```

Add optional configuration to `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "URLSCAN_TIMEOUT": "10"
  }
}
```

### Azure Deployment

Add to Application Settings:
```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --settings URLSCAN_API_KEY="your-api-key"
```

Or via Azure Portal:
1. Navigate to Function App
2. Settings → Configuration
3. Application Settings → New application setting
4. Name: `URLSCAN_API_KEY`, Value: `<your-key>`

## Security Considerations

- API key stored only in environment variables (never in code or logs)
- No sensitive data logged in error messages
- Input validation prevents injection attacks
- HTTPS-only communication with URLScan.io
- Rate limiting handled by upstream API (429 responses caught)
- UUID format validation to prevent path traversal
- Query parameter sanitization for search
- Users responsible for not submitting URLs with PII

## Testing

### Unit Tests (`test_urlscan.py`)
- Mock all HTTP requests using `responses` or `requests-mock`
- Test valid submissions, result retrieval, and searches
- Test parameter validation for all functions
- Test error conditions (missing params, invalid formats, API errors)
- Test timeout handling
- Test rate limiting (429) responses
- Marked with `@pytest.mark.unit`

### Endpoint Tests (`test_urlscan_endpoint.py`)
- Test HTTP request/response handling for all three endpoints
- Test parameter parsing (query string and JSON body)
- Test error mapping to HTTP status codes
- Test 404 handling for result endpoint
- Marked with `@pytest.mark.endpoint`

### Live Tests (`test_urlscan_live.py`)
- Real API calls (requires valid API key)
- Test submission, result retrieval, and search operations
- Use safe, read-only operations
- Skipped in CI/CD pipeline
- Marked with `@pytest.mark.live`

## Usage Examples

### Submit URL

```bash
# Via query parameters
curl -X POST "https://<function-app>.azurewebsites.net/api/urlscan/submit?code=<function-key>&url=https://example.com&visibility=public"

# Via JSON body
curl -X POST "https://<function-app>.azurewebsites.net/api/urlscan/submit?code=<function-key>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "visibility": "unlisted"}'
```

### Retrieve Result

```bash
# Via query parameter
curl "https://<function-app>.azurewebsites.net/api/urlscan/result?code=<function-key>&uuid=abc123-def456-..."

# Via JSON body
curl "https://<function-app>.azurewebsites.net/api/urlscan/result?code=<function-key>" \
  -H "Content-Type: application/json" \
  -d '{"uuid": "abc123-def456-..."}'
```

### Search Scans

```bash
# Via query parameters
curl "https://<function-app>.azurewebsites.net/api/urlscan/search?code=<function-key>&q=domain:example.com&size=10"

# Via JSON body
curl "https://<function-app>.azurewebsites.net/api/urlscan/search?code=<function-key>" \
  -H "Content-Type: application/json" \
  -d '{"q": "domain:example.com", "size": 10}'
```

### Using Python

```python
import requests
import time

base_url = "https://<function-app>.azurewebsites.net/api/urlscan"
params = {"code": "<function-key>"}

# Submit URL
submit_data = {"url": "https://example.com", "visibility": "public"}
response = requests.post(f"{base_url}/submit", params=params, json=submit_data)
result = response.json()
uuid = result['result']['uuid']
print(f"Scan UUID: {uuid}")

# Wait for scan to complete
time.sleep(30)

# Retrieve result
result_data = {"uuid": uuid}
response = requests.get(f"{base_url}/result", params=params, json=result_data)
scan_result = response.json()
print(f"Scan completed: {scan_result['result']['page']['url']}")

# Search for scans
search_data = {"q": "domain:example.com", "size": 5}
response = requests.get(f"{base_url}/search", params=params, json=search_data)
search_results = response.json()
print(f"Found {search_results['result']['total']} scans")
```

## Rate Limiting

URLScan.io enforces rate limits per API key:
- Limits apply per minute, hour, and day
- Limits vary by account type (free vs paid)
- Check quotas: `GET https://urlscan.io/user/quotas/`
- Response headers indicate remaining quota

**Best Practices:**
- Implement exponential backoff on 429 responses
- Search before submitting to avoid duplicates
- Use pagination for large result sets
- Limit search queries by date when possible

## Future Enhancements

Potential improvements (not currently implemented):
- Screenshot and DOM snapshot retrieval endpoints
- Webhook support for scan completion notifications
- Bulk URL submission with batch processing
- Response caching for frequently accessed results
- Retry logic with exponential backoff
- Advanced search filters and aggregations

## Dependencies

- `requests`: HTTP client (already in requirements.txt)
- `azure-functions`: Azure Functions SDK (already in requirements.txt)
- `typing`: Type hints (Python standard library)
- `os`: Environment variables (Python standard library)

No additional dependencies required.

## Integration Points

- Extends existing `functions/urlscan.py` module
- Follows patterns from `functions/abuseipdb.py` and `functions/alienvault.py`
- Compatible with existing error handling in `function_app.py`
- Uses same testing infrastructure as other modules
- Consistent with implementation_pattern.md guidelines

## Deployment Checklist

- [x] Implementation plan documented
- [ ] Code implemented in functions/urlscan.py
- [ ] Routes added to function_app.py
- [ ] Unit tests passing
- [ ] Endpoint tests passing
- [ ] Linting (ruff) passing
- [ ] Type checking (mypy) passing
- [ ] Live tests verified with real API key
- [ ] Environment variable configured in Azure
- [ ] Deployed to staging
- [ ] All endpoints tested in staging
- [ ] README updated with new endpoints

## References

- URLScan.io API Documentation: https://urlscan.io/docs/api/
- URLScan.io Result API Reference: https://urlscan.io/docs/result/
- URLScan.io Search API Reference: https://urlscan.io/docs/search/
- URLScan.io Homepage: https://urlscan.io/
