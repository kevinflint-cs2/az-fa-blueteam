# Examples: DNS Resolver (curl)

Examples demonstrating how to call the asynchronous DNS resolver endpoint.

## 1) Simple POST with single domain

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{ "domains": ["example.com"] }'
```

## 2) POST with multiple domains

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": [
      "example.com",
      "google.com",
      "github.com",
      "cloudflare.com"
    ]
  }'
```

## 3) GET with comma-separated domains

```bash
curl "http://localhost:7071/api/dns/resolve?domains=example.com,google.com,github.com"
```

## 4) POST with custom timeout and retries

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["slow-dns-server.com"],
    "timeout": 10.0,
    "retries": 3
  }'
```

## 5) POST with custom nameservers (Google DNS)

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["example.com"],
    "nameservers": ["8.8.8.8", "8.8.4.4"]
  }'
```

## 6) POST with custom nameservers (Cloudflare DNS)

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["github.com", "gitlab.com"],
    "nameservers": ["1.1.1.1", "1.0.0.1"]
  }'
```

## 7) POST with high concurrency for batch processing

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{
    "domains": ["site1.com", "site2.com", "site3.com"],
    "concurrency": 100,
    "retries": 1
  }'
```

## 8) Example success response (single domain)

```json
[
  {
    "domain": "example.com",
    "resolvable": true,
    "ip_addresses": [
      "93.184.216.34",
      "2606:2800:220:1:248:1893:25c8:1946"
    ],
    "name_servers": [
      "a.iana-servers.net.",
      "b.iana-servers.net."
    ],
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

## 9) Example response with multiple domains (mixed success/failure)

```json
[
  {
    "domain": "example.com",
    "resolvable": true,
    "ip_addresses": ["93.184.216.34"],
    "name_servers": ["a.iana-servers.net.", "b.iana-servers.net."],
    "dnssec": "signed-present",
    "error": null,
    "metrics": {
      "duration_ms": 156,
      "query_count": null,
      "retries": 0,
      "resolved_by_nameserver": "8.8.8.8"
    },
    "trace": {
      "trace_id": null,
      "span_id": "span-abc123",
      "parent_span_id": null,
      "nameserver": "8.8.8.8"
    }
  },
  {
    "domain": "notfound.invalid",
    "resolvable": false,
    "ip_addresses": [],
    "name_servers": [],
    "dnssec": "unknown",
    "error": {
      "type": "NXDOMAIN",
      "message": "The DNS query name does not exist: notfound.invalid.",
      "attempts": 1,
      "last_nameserver": "8.8.8.8"
    },
    "metrics": {
      "duration_ms": 89,
      "query_count": null,
      "retries": 0,
      "resolved_by_nameserver": "8.8.8.8"
    },
    "trace": {
      "trace_id": null,
      "span_id": "span-def456",
      "parent_span_id": null,
      "nameserver": "8.8.8.8"
    }
  }
]
```

## 10) Example IPv4-only domain response

```json
[
  {
    "domain": "ipv4only.example.com",
    "resolvable": true,
    "ip_addresses": ["203.0.113.42"],
    "name_servers": ["ns1.example.com.", "ns2.example.com."],
    "dnssec": "unsigned",
    "error": null,
    "metrics": {
      "duration_ms": 178,
      "query_count": null,
      "retries": 0,
      "resolved_by_nameserver": "8.8.8.8"
    },
    "trace": {
      "trace_id": null,
      "span_id": "span-789abc",
      "parent_span_id": null,
      "nameserver": "8.8.8.8"
    }
  }
]
```

## 11) Example IPv6-only domain response

```json
[
  {
    "domain": "ipv6only.example.com",
    "resolvable": true,
    "ip_addresses": ["2001:db8::1"],
    "name_servers": ["ns1.example.com.", "ns2.example.com."],
    "dnssec": "unsigned",
    "error": null,
    "metrics": {
      "duration_ms": 203,
      "query_count": null,
      "retries": 0,
      "resolved_by_nameserver": "2001:4860:4860::8888"
    },
    "trace": {
      "trace_id": null,
      "span_id": "span-xyz789",
      "parent_span_id": null,
      "nameserver": "2001:4860:4860::8888"
    }
  }
]
```

## 12) Example error response (missing domains parameter)

```bash
curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response (HTTP 400):
```
Missing required parameter: domains (array)
```

## 13) Batch processing 100 domains

```bash
# Generate list of domains (example using jq)
domains=$(echo '["site1.com", "site2.com", "site3.com"]' | jq -c '.')

curl -X POST "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d "{\"domains\": $domains, \"concurrency\": 50}"
```

## Notes

- The Functions host must be running locally for `localhost:7071` examples to work
- For production, replace `http://localhost:7071` with your deployed function URL
- Response is always HTTP 200 unless there's a malformed request (400) or internal error (500)
- Per-domain errors are returned in the `error` field, not as HTTP errors
- Domains are resolved in parallel with configurable concurrency
- Results are returned in the same order as the input `domains` array

## Performance Tips

- **Batch requests**: Send up to 100-1000 domains per request for best efficiency
- **Adjust concurrency**: Increase `concurrency` for faster batch processing (default: 50)
- **Use retries**: Set `retries: 2-3` for unreliable networks (default: 2)
- **Custom nameservers**: Use geographically close nameservers for lower latency
- **Timeout tuning**: Increase `timeout` for slow DNS servers, decrease for fast responses

## DNSSEC Validation

The resolver performs **presence-based DNSSEC detection only**:
- Checks for RRSIG and DNSKEY records
- Returns `"signed-present"` if found, `"unsigned"` if not found
- Does not perform cryptographic validation
- Use `dnssec: "signed-present"` as a heuristic, not proof of validity
