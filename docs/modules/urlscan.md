# URLScan.io Submission Endpoint

User-facing documentation for the URLScan.io submission endpoint implemented in `functions/urlscan.py`.

## Purpose

Submit URLs to URLScan.io for automated scanning and threat analysis. The endpoint returns a submission UUID and result URL immediately, allowing you to retrieve detailed scan results later via the URLScan.io website or API.

## Route

- `POST /api/urlscan/submit`

Accepts parameters via query string or JSON body.

## Parameters

- `url` (string, required) — The URL to scan (must be a valid HTTP/HTTPS URL).
- `visibility` (string, optional) — Scan visibility: `public`, `unlisted`, or `private` (default: `public`).
  - `public`: Scan results are publicly visible and indexed
  - `unlisted`: Scan results are not indexed but accessible via direct link
  - `private`: Scan results are only visible to the API key owner

## Example Requests

See `docs/examples/urlscan-curl.md` for detailed curl examples.

### Quick Examples

#### Using Query Parameters
```bash
curl -X POST "http://localhost:7071/api/urlscan/submit?url=https://example.com&visibility=unlisted"
```

### Using JSON Body
```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "visibility": "private"}'
```

### Using Default Visibility (Public)
```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Response Format

### Success Response (HTTP 200)

```json
{
  "status": "ok",
  "result": {
    "message": "Submission successful",
    "uuid": "019a8824-d1f8-7049-8e0d-cea598735489",
    "result": "https://urlscan.io/result/019a8824-d1f8-7049-8e0d-cea598735489/",
    "api": "https://urlscan.io/api/v1/result/019a8824-d1f8-7049-8e0d-cea598735489/",
    "visibility": "unlisted",
    "url": "https://example.com/"
  }
}
```

**Response Fields:**
- `uuid`: Unique identifier for the scan
- `result`: Web URL to view scan results in browser
- `api`: API endpoint to retrieve scan results programmatically
- `visibility`: Confirmed visibility setting
- `url`: The URL that was submitted (normalized)

### Error Responses

**Missing URL (HTTP 400)**
```json
{
  "status": "error",
  "error": {
    "msg": "missing 'url' parameter"
  }
}
```

**Invalid Visibility (HTTP 400)**
```json
{
  "status": "error",
  "error": {
    "msg": "visibility must be one of ['public', 'unlisted', 'private'], got 'invalid'"
  }
}
```

**API Error (HTTP 500)**
```json
{
  "status": "error",
  "error": {
    "msg": "URLScan.io API rate limit exceeded. Try again later."
  }
}
```

## Configuration (Environment Variables)

### Required
- `URLSCAN_API_KEY` — Your URLScan.io API key (obtain from https://urlscan.io/user/profile)

### Optional
- `URLSCAN_TIMEOUT` — Request timeout in seconds (default: 10)

### Local Development Setup
```bash
func settings add URLSCAN_API_KEY "your-api-key-here"
```

### Azure Production Setup
Add to Application Settings in Azure Portal or via CLI:
```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --settings URLSCAN_API_KEY="your-api-key"
```

## Retrieving Scan Results

Scan results are typically available within 10-30 seconds after submission. Use the returned `result` URL to view in a browser, or use the `api` URL to retrieve JSON results programmatically.

### Example: Retrieve Results via API
```bash
# Wait 15-30 seconds after submission, then:
curl "https://urlscan.io/api/v1/result/019a8824-d1f8-7049-8e0d-cea598735489/"
```

> [!NOTE]
> This endpoint only submits URLs for scanning. To retrieve results, use the URLScan.io API directly with the returned UUID.

## Error Handling

The endpoint handles various error conditions:

- **400 (Bad Request)**: Missing or invalid parameters
- **401 (Unauthorized)**: Invalid API key
- **429 (Rate Limited)**: URLScan.io rate limit exceeded
- **500 (Internal Server Error)**: Network errors or URLScan.io service issues

## Security Considerations

- API key is stored securely in environment variables
- Never log or expose API keys in error messages
- Scan visibility controls who can view results:
  - Use `private` for sensitive URLs
  - Use `unlisted` for internal investigations
  - Use `public` only for confirmed malicious URLs you want to share

> [!WARNING]
> Submitting URLs to URLScan.io will cause the service to visit and render those URLs. Do not submit URLs containing sensitive information or authentication tokens unless using `private` visibility.

## Rate Limits

URLScan.io applies rate limits based on your account tier:
- Free tier: Limited submissions per day
- Paid tiers: Higher limits with faster scanning

The endpoint will return a 500 error with a clear message if rate limits are exceeded.

## Troubleshooting

### "URLScan.io API key not set"
Ensure `URLSCAN_API_KEY` is configured in your environment. For local development, use `func settings add`. For Azure, add to Application Settings.

### "URLScan.io API authentication failed"
Verify your API key is valid. Generate a new key from your URLScan.io profile if needed.

### "URLScan.io API request timed out"
The submission request took too long. Check your network connectivity and consider increasing `URLSCAN_TIMEOUT`.

### Results not available immediately
Scans typically complete within 10-30 seconds. Wait briefly before retrieving results via the returned API URL.

## Implementation & Tests

- **Implementation**: `functions/urlscan.py`
- **Implementation Documentation**: `docs/implementation/urlscan.md`
- **Unit Tests**: `tests/test_urlscan.py` (mocked external API calls)
- **Endpoint Tests**: `tests/test_urlscan_endpoint.py` (HTTP endpoint behavior)
- **Live Tests**: `tests/test_urlscan_live.py` (marked with `@pytest.mark.endpoint`)

## Related Resources

- [URLScan.io API Documentation](https://urlscan.io/docs/api/)
- [URLScan.io Submission API](https://urlscan.io/docs/api/#submission)
- [URLScan.io Result Retrieval](https://urlscan.io/docs/api/#result)
