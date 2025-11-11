## Whois / RDAP implementation (combined `/api/whois` endpoint)

This document describes the implementation design for a single combined whois endpoint that accepts either an IP address or a domain name and returns a normalized JSON result. It mirrors the Phase 3 design and is intended to be included with the code before implementation.

### Goal

- Provide a single endpoint `/api/whois` that accepts a `q` parameter (domain or IP), auto-detects the type, fetches RDAP for IPs and WHOIS/RDAP for domains, normalizes output to a consistent schema, supports optional raw output and caching, and maps errors to sensible HTTP statuses.

### File layout (planned)

- `functions/whois.py` — main module implementing detection, fetchers, normalization, caching, and export `handle_request(payload: dict) -> dict`.
- `function_app.py` — add route `/api/whois` to call `functions.whois.handle_request` following existing routing conventions.
- `tests/test_whois.py` — unit tests (mocked network calls).
- `tests/test_whois_live.py` — optional live tests (marked `@pytest.mark.live`).

### Dependencies

- Standard library: `ipaddress`, `logging`, `datetime`, `typing`.
- Runtime packages to add (recommended):
  - `ipwhois` (RDAP for IPs)
  - `whois` (domain whois parsing)
  - `tldextract` (robust domain parsing and IDN handling)
  - `cachetools` (optional, TTL cache)
  - `requests` (already present in repo)

Update `requirements.txt` when implementing.

### Configuration / Environment

- `WHOIS_CACHE_TTL` — TTL for in-memory cache in seconds (default: 86400).
- `WHOIS_PREFER_RDAP` — prefer RDAP when available (default: "true").
- `WHOIS_MAX_TIMEOUT` — default timeout for external calls in seconds (default: 10).

If a third-party WHOIS/RDAP provider is used later, add env vars such as `WHOIS_API_KEY` and `WHOIS_API_URL`.

### Function contract

Module: `functions/whois.py`

Public:
- def handle_request(payload: dict) -> dict
  - Required key: `q` (string) — the query (domain or IP).
  - Optional keys: `source` ("rdap"|"whois"|"auto"), `raw` (bool), `timeout` (int seconds).
  - Returns JSON-serializable dict with either `status: "ok"` and `result` or `status: "error"` and `error` following project conventions.

Error mapping (handled by `function_app.py` per repo pattern):
- `ValueError` -> HTTP 400
- Rate-limited upstream -> HTTP 429
- Upstream timeouts -> HTTP 504
- Unexpected -> HTTP 500

### Detection logic

- Use `ipaddress` to detect IPv4/IPv6.
- For domain validation, use `tldextract` and a minimal regex; support IDN/punycode normalization.
- If detection fails -> raise ValueError.

### Fetchers & normalization

IP path (preferred: RDAP):
- `fetch_rdap_for_ip(ip: str, timeout: int) -> tuple[dict, dict]` — returns (normalized_data, raw_rdap_json).
- Use `ipwhois` RDAP client for structured JSON; normalize fields.

Domain path (WHOIS/RDAP):
- `fetch_whois_for_domain(domain: str, timeout: int) -> tuple[dict, str]` — returns (normalized_data, raw_text).
- Prefer RDAP when available for structured data; otherwise use `whois` package and parse text.

Normalization helpers produce a consistent `data` dict (see schema below).

### Canonical `result` schema

Top-level response:

{ "status": "ok", "result": { "query": "...", "type": "ip|domain", "source": "rdap|whois|rdap+whois", "fetched_at": "ISO8601", "data": { ... }, "raw": <optional> } }

Normalized `data` fields (not all fields are always present):

- Common / domain-focused:
  - `domain_name` (str)
  - `registrar`, `registrar_id`, `registry_domain_id`
  - `status_list` (list[str])
  - `dnssec` (str|null)
  - `created_on`, `updated_on`, `expires_on` (ISO8601|null)
  - `nameservers` (list[str])
  - `registrant`, `admin`, `tech`, `abuse_contact` (objects with name, org, email, phone, street, city, state, postal_code, country)
  - `emails` (list[str]) — aggregated contact emails
  - `tld_specific` (dict)

- IP / RDAP-focused:
  - `inetnum_start`, `inetnum_end` (str)
  - `cidr` (str|null)
  - `netname`, `handle` (str|null)
  - `country` (str|null)
  - `org_name`, `org_handle` (str|null)
  - `status_list` (list[str])
  - `abuse_emails` (list[str])
  - `contacts` (admin/tech/abuse) — each with handle/email/phone
  - `asn` (int|null) optionally if resolvable

- Provenance (always present):
  - `source` (rdap|whois|rdap+whois)
  - `fetched_at` (ISO8601 UTC)
  - `query` (original)

Notes:
- Use `null` for missing scalars and empty lists for missing repeated fields.
- Normalize timestamps to ISO8601 UTC where possible.

### Edge cases & policy notes

- Reserved/private IPs (RFC1918/loopback): return `type: "ip"` and `data: { "reserved": true }` (recommended) rather than an error.
- IDN domains: normalize using punycode for lookups but return human-readable `domain_name` where appropriate.
- GDPR/redaction: many WHOIS fields may be missing or redacted — treat as `null`.
- Multi-format WHOIS responses: normalize repeated fields to lists.
- Rate limiting: implement caching and propagate `Retry-After` when upstream provides it.

### Caching

- Implement a module-level TTL cache keyed by normalized query and `source` option.
- Use `WHOIS_CACHE_TTL` env var (default 24h) and `cachetools.TTLCache` or a small in-memory wrapper.

### Logging & observability

- Log query (truncated/masked), detected type, chosen source, latency, and error codes.
- Do not log raw WHOIS content by default. If `raw=true` is requested, avoid logging full raw content (or redact emails).
- Optionally emit metrics for counts, durations, and upstream error classes if metrics infrastructure exists.

### Security & privacy

- Raw whois output must be opt-in (`raw=true`). Do not persist raw responses unless explicitly configured.
- Avoid logging PII (emails, full names) — mask or redact in logs.

### Testing

- Unit tests (mocked external calls):
  - missing `q` -> ValueError -> HTTP 400 mapping
  - invalid `q` -> HTTP 400
  - detection (IP vs domain)
  - normalized output for sample RDAP JSON and WHOIS text
  - reserved IP handling
  - upstream timeout/429 handling
  - cache hit behavior

- Live tests (optional, `@pytest.mark.live`):
  - a couple of canonical domains (e.g., `example.com`) and public IPs (e.g., `8.8.8.8`) — run only in gated CI or locally.

Testing notes: mock `ipwhois` and `whois` clients using `pytest-mock` or `responses`.

### Example requests & responses

Request (body or query param):

```json
{ "q": "example.com", "raw": false }
```

Example domain response (trimmed):

```json
{
  "status": "ok",
  "result": {
    "query": "example.com",
    "type": "domain",
    "source": "whois",
    "fetched_at": "2025-11-11T12:34:56Z",
    "data": {
      "domain_name": "example.com",
      "registrar": "IANA",
      "created_on": "1995-08-13T00:00:00Z",
      "expires_on": "2026-08-13T00:00:00Z",
      "nameservers": ["a.iana-servers.net", "b.iana-servers.net"]
    }
  }
}
```

Example IP response (trimmed):

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
      "inetnum_start": "8.8.8.0",
      "inetnum_end": "8.8.8.255",
      "netname": "GOOGLE",
      "country": "US",
      "org_name": "Google LLC",
      "abuse_emails": ["network-abuse@google.com"]
    }
  }
}
```

### Phased implementation steps (low-risk rollout)

1. Create `functions/whois.py` skeleton with `handle_request`, detection, and stubbed fetchers that return predictable normalized shapes; add unit tests exercising detection and normalization stubs.
2. Implement RDAP lookup for IPs using `ipwhois` and normalization.
3. Implement domain WHOIS via `whois` (and RDAP fallback) and normalization.
4. Add caching, raw output option, and TTL configuration.
5. Add live tests (gated), update `requirements.txt`, run `ruff`/`mypy`, and add docs (this file).

### Risks & mitigations

- WHOIS format variability: favor RDAP where available; keep `raw` fallback so consumers can re-parse if needed.
- Rate-limiting: cache results and consider adding retries/backoff or a third-party provider if heavy traffic is expected.
- PII exposure: require `raw=true` to include raw text and redact in logs; document privacy implications.

### Next steps

- This file documents the Phase 3 plan. After review or approval, proceed to Phase 4 to implement code: add `functions/whois.py`, wire the route in `function_app.py`, add unit tests under `tests/`, update `requirements.txt`, and run tests and linters.
