# Examples: URLScan.io Submission (curl)

Examples demonstrating how to call the URLScan.io submission endpoint.

## 1) Simple POST with JSON body (default public visibility)

```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://example.com" }'
```

## 2) POST with unlisted visibility

```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://suspicious-site.com", "visibility": "unlisted" }'
```

## 3) POST with private visibility (most secure)

```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://internal-site.company.com", "visibility": "private" }'
```

## 4) Using query parameters

```bash
curl -X POST "http://localhost:7071/api/urlscan/submit?url=https://example.com&visibility=unlisted"
```

## 5) Example success response

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

## 6) Retrieving scan results (after 15-30 seconds)

```bash
# Use the 'api' URL from the submission response
curl "https://urlscan.io/api/v1/result/019a8824-d1f8-7049-8e0d-cea598735489/"
```

## 7) Example error response (missing URL)

```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response:
```json
{
  "status": "error",
  "error": {
    "msg": "missing 'url' parameter"
  }
}
```

## 8) Example error response (invalid visibility)

```bash
curl -X POST "http://localhost:7071/api/urlscan/submit" \
  -H "Content-Type: application/json" \
  -d '{ "url": "https://example.com", "visibility": "secret" }'
```

Response:
```json
{
  "status": "error",
  "error": {
    "msg": "visibility must be one of ['public', 'unlisted', 'private'], got 'secret'"
  }
}
```

## Notes

- The Functions host must be running locally for `localhost:7071` examples to work.
- The `URLSCAN_API_KEY` environment variable must be configured.
- For production, replace `http://localhost:7071` with your deployed function URL.
- Scan results are typically available 10-30 seconds after submission.
- Use the `result` URL to view in a browser, or the `api` URL for programmatic access.

## Visibility Recommendations

- **public**: Use for confirmed malicious URLs you want to share publicly
- **unlisted**: Use for internal investigations (results not indexed but accessible via direct link)
- **private**: Use for sensitive URLs or when testing (results only visible to your account)
