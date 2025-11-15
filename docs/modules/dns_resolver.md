# DNS Resolver Endpoint

User-facing documentation for the asynchronous DNS resolver endpoint implemented in `functions/dns_resolver.py`.

## Purpose

Provide a high-performance HTTP endpoint that resolves multiple domain names concurrently, returning structured DNS information including IP addresses (A/AAAA records), nameservers (NS records), basic DNSSEC presence detection, and detailed observability data (metrics, errors, tracing).

## Route

- `POST /api/dns/resolve`
- `GET /api/dns/resolve?domains=example.com,google.com`

Accepts domain names either as a query parameter (comma-separated) or in the JSON request body.

## Parameters

### Required
- `domains` (array of strings or comma-separated string) — list of domain names to resolve

### Optional
- `timeout` (float, default: 3.0) — per-query timeout in seconds
- `per_domain_timeout` (float, default: None) — overall timeout per domain in seconds
- `concurrency` (int, default: 50) — maximum concurrent domain lookups
- `nameservers` (array of strings, default: system resolvers) — custom DNS nameserver IPs
- `retries` (int, default: 2) — number of retry attempts for transient errors
- `cache_ttl_default` (int, default: 60) — default cache TTL in seconds
- `dnssec_mode` (string, default: "presence") — DNSSEC detection mode (Level 1 presence check)

## Example Requests

See `docs/examples/dns-resolver-curl.md` for comprehensive curl examples.

### Quick Examples

#### POST with JSON body
```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["example.com", "google.com"],
    "timeout": 5.0,
    "retries": 1
  }'
```

### GET with query parameters
```bash
curl "http://localhost:7071/api/dns/resolve?domains=example.com,google.com"
```

## Response Format

Returns HTTP 200 with a JSON array containing one result object per domain (in input order):

```json
[
  {
    "domain": "example.com",
    "resolvable": true,
    "ip_addresses": ["93.184.216.34", "2606:2800:220:1:248:1893:25c8:1946"],
    "name_servers": ["a.iana-servers.net.", "b.iana-servers.net."],
    "dnssec": "signed-present",
    "error": null,
    "metrics": {
      "duration_ms": 245,
      "query_count": null,
      "retries": 0,
      "resolved_by_nameserver": "8.8.8.8"
    },
    "trace": {
      "trace_id": null,
      "span_id": "span-1a2b3c4d",
      "parent_span_id": null,
      "nameserver": "8.8.8.8"
    }
  }
]
```

### Response Fields

- `domain` — the queried domain name
- `resolvable` — `true` if at least one IP address was found, `false` otherwise
- `ip_addresses` — array of IPv4 (A) and IPv6 (AAAA) addresses
- `name_servers` — array of authoritative nameservers (NS records)
- `dnssec` — DNSSEC status: `"signed-present"`, `"unsigned"`, or `"unknown"`
- `error` — structured error object or `null` if no error occurred
- `metrics` — performance and retry metrics
- `trace` — distributed tracing identifiers

### Error Format

When a domain cannot be resolved, the `error` field contains:

```json
{
  "type": "NXDOMAIN",
  "message": "The DNS query name does not exist: notfound.example.",
  "attempts": 1,
  "last_nameserver": "8.8.8.8"
}
```

Error types include:
- `NXDOMAIN` — domain does not exist
- `NoAnswer` — domain exists but has no A/AAAA records
- `Timeout` — query timed out after retries
- `NoNameservers` — all nameservers failed (SERVFAIL)
- `LifetimeTimeout` — overall resolution lifetime expired

## IPv4-Only and IPv6-Only Domains

> [!NOTE]
> The resolver correctly handles domains that only have IPv4 (A) records or only IPv6 (AAAA) records. A domain is marked as `resolvable: true` if **either** A or AAAA records are found. The absence of one record type (which returns a DNS NoAnswer response) is treated as normal and does not cause the resolution to fail.

This behavior was fixed in a recent update. Previously, domains with only A records or only AAAA records were incorrectly marked as not resolvable.

## DNSSEC Detection (Level 1)

The resolver performs **presence-based DNSSEC detection** only:
- Queries for RRSIG and DNSKEY records
- If present, marks the domain as `"signed-present"`
- If absent, marks as `"unsigned"`
- If the query fails, marks as `"unknown"`

**No cryptographic validation is performed.** This is a fast heuristic to indicate whether a zone appears to be DNSSEC-signed.

## Configuration

The resolver uses sensible defaults and does not require environment variables. All parameters can be overridden per-request.

### Optional Environment Variables

While not currently implemented, future versions may support:
- `DNS_DEFAULT_TIMEOUT` — default per-query timeout
- `DNS_DEFAULT_CONCURRENCY` — default concurrency limit
- `DNS_CACHE_TTL` — default cache TTL

## Error Handling

- **HTTP 400** — Invalid input (missing domains, invalid parameter types)
- **HTTP 500** — Internal server error
- **Per-domain errors** — Returned in each domain's `error` field, not as HTTP errors

The endpoint returns HTTP 200 even if some domains fail to resolve. Check the `resolvable` field and `error` object for each domain.

## Caching

The resolver uses an in-memory TTL cache to avoid duplicate queries within the same request:
- Cached by (domain, record_type) tuple
- Respects DNS TTL values from responses
- Falls back to `cache_ttl_default` if TTL is unavailable
- Cache is not shared across requests

## Performance Characteristics

- **Concurrency**: Resolves multiple domains in parallel (default: 50 concurrent)
- **Retries**: Automatically retries transient errors (SERVFAIL, timeouts) with exponential backoff
- **Timeouts**: Conservative per-query timeout (default: 3 seconds)
- **CNAME following**: Follows CNAME chains up to 8 levels deep with loop detection

### Typical Latency
- Single domain: 50-300ms
- Batch of 100 domains: 2-5 seconds (depending on DNS response times)

## Troubleshooting

### Domain Marked as Not Resolvable

1. **Check the `error` field** — it contains the specific DNS error (NXDOMAIN, NoAnswer, Timeout, etc.)
2. **Verify the domain exists** — use `dig` or `nslookup` to confirm
3. **Check for IPv4/IPv6 only** — domains with only A or only AAAA records are correctly handled
4. **Review timeout settings** — increase `timeout` or `retries` for slow DNS servers

### DNSSEC Shows "unknown"

- The DNSSEC query (RRSIG/DNSKEY) failed or timed out
- This does not affect IP resolution
- Consider increasing timeout for DNSSEC queries

### Slow Performance

- Reduce `concurrency` if overwhelming DNS servers
- Use custom `nameservers` that are geographically closer
- Enable DNS caching at the infrastructure level

### Private/Internal Domains

- The resolver returns private IP addresses (10.x.x.x, 192.168.x.x, etc.) without filtering
- Consider filtering results in your application if needed

## Implementation Details

- **Library**: `dnspython` with async resolver (`dns.asyncresolver`)
- **Concurrency**: `asyncio` with semaphore-based limiting
- **Tests**: See `tests/test_dns_resolver.py` for unit tests and `tests/test_dns_resolver_live.py` for live endpoint tests

For design details and implementation decisions, see `docs/prompts/dns_resolver.md`.
