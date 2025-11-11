# Examples: Whois endpoint (curl)

Examples demonstrating how to call the combined Whois / RDAP endpoint.

1) Simple GET (query param)

```bash
curl "http://localhost:7071/api/whois?q=example.com"
```

2) POST JSON body (domain) — request raw whois text

```bash
curl -X POST "http://localhost:7071/api/whois" \
  -H "Content-Type: application/json" \
  -d '{ "q": "example.com", "raw": true }'
```

3) POST JSON body (IP) — force RDAP source

```bash
curl -X POST "http://localhost:7071/api/whois" \
  -H "Content-Type: application/json" \
  -d '{ "q": "8.8.8.8", "source": "rdap" }'
```

4) Example response (trimmed)

```json
{
  "status": "ok",
  "result": {
    "query": "8.8.8.8",
    "type": "ip",
    "source": "rdap",
    "fetched_at": "2025-11-11T12:34:56Z",
    "data": {
      "cidr": "8.8.8.0/24",
      "netname": "GOOGLE",
      "country": "US",
      "abuse_emails": ["network-abuse@google.com"]
    }
  }
}
```

Notes
- The Functions host must be running locally for the `localhost:7071` examples to work.
- For live tests and production, replace `http://localhost:7071` with your deployed function URL and ensure any required environment settings are in place.
