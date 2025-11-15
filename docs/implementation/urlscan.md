# URLScan.io Submission Implementation

## Overview

This document describes the implementation of the URLScan.io submission endpoint for the Azure Functions BlueTeam enrichment application.

## Implementation Option Selected

**Option A: Standard Azure Function with Submission-Only Pattern**

This option was selected because it:
- Matches existing patterns in the repository (abuseipdb, alienvault)
- Provides focused, single-responsibility functionality
- Keeps initial implementation simple and maintainable
- Allows incremental addition of result retrieval if needed later

## Architecture

### Module Structure

**File:** `functions/urlscan.py`

**Functions:**
- `submit_url(url: str, visibility: str = "public") -> dict[str, Any]`
  - Core business logic for submitting URLs to URLScan.io
  - Validates parameters and makes API request
  - Returns parsed API response
  
- `handle_request(payload: dict[str, Any]) -> dict[str, Any]`
  - Entry point called by `function_app.py`
  - Validates payload structure
  - Delegates to `submit_url`
  - Returns standardized response format

### HTTP Endpoint

**Route:** `/api/urlscan/submit`  
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

Error (HTTP 400/500):
```json
{
  "status": "error",
  "error": {
    "msg": "missing 'url' parameter"
  }
}
```

## API Integration

### URLScan.io API Details

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

### Error Handling

**Client Errors (HTTP 400):**
- Missing `url` parameter
- Invalid `visibility` value (not "public", "unlisted", or "private")

**Server Errors (HTTP 500):**
- Missing `URLSCAN_API_KEY` environment variable
- URLScan.io API errors (rate limiting, authentication, service issues)

## Configuration

### Environment Variables

**Required:**
- `URLSCAN_API_KEY`: API key from URLScan.io account

**Optional:**
- `URLSCAN_TIMEOUT`: Request timeout in seconds (default: 10)

### Local Development Setup

Add to `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "URLSCAN_API_KEY": "your-api-key-here"
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

- API key stored only in environment variables
- No sensitive data logged in error messages
- Input validation prevents injection attacks
- HTTPS-only communication with URLScan.io
- Rate limiting handled by upstream API (429 responses caught)

## Testing

### Unit Tests (`test_urlscan.py`)
- Mock all HTTP requests
- Test valid submissions
- Test parameter validation
- Test error conditions

### Endpoint Tests (`test_urlscan_endpoint.py`)
- Test HTTP request/response handling
- Test parameter parsing (query string and JSON)
- Test error mapping to HTTP status codes

### Live Tests (`test_urlscan_live.py`)
- Marked with `@pytest.mark.live`
- Real API calls (requires valid API key)
- Skipped in CI/CD pipeline

## Usage Examples

### Using curl

```bash
# Submit via query parameters
curl -X POST "https://<function-app>.azurewebsites.net/api/urlscan/submit?code=<function-key>&url=https://example.com&visibility=public"

# Submit via JSON body
curl -X POST "https://<function-app>.azurewebsites.net/api/urlscan/submit?code=<function-key>" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "visibility": "unlisted"}'
```

### Using Python

```python
import requests

url = "https://<function-app>.azurewebsites.net/api/urlscan/submit"
params = {"code": "<function-key>"}
data = {
    "url": "https://example.com",
    "visibility": "public"
}

response = requests.post(url, params=params, json=data)
result = response.json()
print(f"Scan UUID: {result['result']['uuid']}")
print(f"Results URL: {result['result']['url']}")
```

## Future Enhancements

- Add result retrieval endpoint (`/api/urlscan/result`)
- Implement caching for repeated URL submissions
- Add webhook support for scan completion notifications
- Support batch URL submissions
- Add screenshot retrieval functionality

## Dependencies

- `requests`: HTTP client (already in requirements.txt)
- `azure-functions`: Azure Functions SDK (already in requirements.txt)

## Integration Points

- Follows patterns from `functions/abuseipdb.py` and `functions/alienvault.py`
- Compatible with existing error handling in `function_app.py`
- Uses same testing infrastructure as other modules

## Deployment Checklist

- [x] Code implemented and tested locally
- [ ] Unit tests passing
- [ ] Linting (ruff) passing
- [ ] Type checking (mypy) passing
- [ ] Live tests verified with real API key
- [ ] Documentation complete
- [ ] Environment variable configured in Azure
- [ ] Deployed to staging
- [ ] Endpoint tested in staging environment
- [ ] README updated with new endpoint

## References

- URLScan.io API Documentation: https://urlscan.io/docs/api/
- URLScan.io Submission API: https://urlscan.io/docs/api/#submission
