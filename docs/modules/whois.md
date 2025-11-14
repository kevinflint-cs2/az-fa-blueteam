# Whois / RDAP Endpoint

User-facing documentation for the combined Whois / RDAP endpoint implemented in `functions/whois.py`.

## Purpose

Provide a single, simple HTTP endpoint that accepts either an IP address or a domain name and returns a normalized JSON result with WHOIS or RDAP information.

## Route

- `POST /api/whois` or `GET /api/whois?q=<query>`

Accepts the query as either a query parameter `q` or in the JSON body.

## Parameters

- `q` (string, required) — the query; either a domain (e.g., `example.com`) or an IP address (e.g., `8.8.8.8`).
- `source` (optional) — `rdap`, `whois`, or `auto` (default: `auto`).
- `raw` (optional, boolean) — include raw WHOIS/RDAP text/JSON in the response when true (default: false).
- `timeout` (optional, integer seconds) — override external lookup timeout (server may cap this).

## Example requests

See the example file: `docs/examples/whois-curl.md` for curl examples and JSON body forms.

## Response shape

Success response (HTTP 200) follows the repo contract:

```json
{
  "status": "ok",
  "result": {
    "query": "example.com",
    "type": "domain",
    "source": "whois",
    "fetched_at": "2025-11-11T12:34:56Z",
    "data": { /* normalized fields */ },
    "raw": "..." // optional when requested
  }
}
```

On error the endpoint returns `status: error` with an `error` object and appropriate HTTP status codes:

- 400: missing or invalid `q` parameter
- 429: upstream/provider rate limit
- 504: upstream timeout
- 500: internal/unexpected error

## Normalized fields

The `data` object contains normalized attributes depending on the query type. Examples:

- Domain: `domain_name`, `registrar`, `created_on`, `expires_on`, `nameservers`, `registrant` (object), `emails` (list)
- IP (RDAP): `cidr`, `inetnum_start`, `inetnum_end`, `netname`, `country`, `org_name`, `abuse_emails` (list)

Fields may be `null` or omitted when not available (GDPR redaction, TLD quirks).

## Configuration (env vars)

- `WHOIS_CACHE_TTL` — optional TTL (seconds) for in-process cache (default: 86400 = 24h).
- `WHOIS_PREFER_RDAP` — optional, `true`/`false` to prefer RDAP when available (default: `true`).
- `WHOIS_MAX_TIMEOUT` — optional default timeout for external lookups (seconds, default: 10).

## Security & privacy

- Raw WHOIS text can contain PII. `raw=true` must be explicitly requested and responses should be treated as sensitive.
- Do not log raw responses in production without redaction and access controls.

## Troubleshooting / Limitations

- WHOIS formats vary by TLD; RDAP is preferred for structured IP data.
- Private/reserved IP ranges are handled specially and return `{ "reserved": true }`.
- Rate limits may apply; enable caching (default TTL) for heavy workloads.

## Implementation & tests

- Implementation: `functions/whois.py` (see `docs/implementation/whois.md` for design details).
- Unit tests: `tests/test_whois.py` (mocked tests) and live tests are marked `@pytest.mark.live`.
