# AbuseIPDB Endpoints

User-facing documentation for the AbuseIPDB integration endpoints implemented in `functions/abuseipdb.py`.

## Purpose

Query and report IP addresses to AbuseIPDB for reputation checking and abuse reporting. AbuseIPDB is a community-driven IP address reputation database used to identify and report malicious IP addresses.

## Routes

- `GET /api/abuseipdb/check` — Check IP address reputation
- `POST /api/abuseipdb/report` — Report malicious IP address

Both routes accept parameters via query string or JSON body.

## Check IP Endpoint

### Parameters

- `ip` (string, required) — The IP address to check (IPv4 or IPv6)

### Example Requests

See `docs/examples/abuseipdb-curl.md` for detailed curl examples.

#### Quick Examples

**Using Query Parameter:**
```bash
curl "http://localhost:7071/api/abuseipdb/check?ip=8.8.8.8"
```

**Using JSON Body:**
```bash
curl -X POST "http://localhost:7071/api/abuseipdb/check" \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'
```

### Response Format

**Success (HTTP 200):**
```json
{
  "data": {
    "ipAddress": "8.8.8.8",
    "isPublic": true,
    "ipVersion": 4,
    "isWhitelisted": true,
    "abuseConfidenceScore": 0,
    "countryCode": "US",
    "usageType": "Content Delivery Network",
    "isp": "Google LLC",
    "domain": "google.com",
    "totalReports": 0,
    "numDistinctUsers": 0,
    "lastReportedAt": null
  }
}
```

**Response Fields:**
- `ipAddress` — The queried IP address
- `isPublic` — Whether the IP is public (not private/reserved)
- `abuseConfidenceScore` — 0-100 score indicating likelihood of abuse (0 = clean, 100 = definitely malicious)
- `isWhitelisted` — Whether the IP is on AbuseIPDB's whitelist
- `countryCode` — Two-letter country code
- `usageType` — Type of IP usage (e.g., "Data Center", "ISP", "CDN")
- `isp` — Internet Service Provider name
- `domain` — Associated domain name
- `totalReports` — Total number of abuse reports (last 90 days by default)
- `numDistinctUsers` — Number of distinct reporters
- `lastReportedAt` — ISO timestamp of most recent report

### Error Responses

**Missing IP (HTTP 400):**
```
Missing required parameter: ip
```

**API Error (HTTP 500):**
```
Error: AbuseIPDB check failed: 401 Unauthorized
```

## Report IP Endpoint

### Parameters

- `ip` (string, required) — The IP address to report
- `categories` (string, required) — Comma-separated category IDs
- `comment` (string, required) — Description of the abuse

### Category IDs

Common AbuseIPDB category IDs:
- `3` — Fraud Orders
- `4` — DDoS Attack
- `9` — Hacking
- `10` — Spam
- `14` — Port Scan
- `15` — Brute-Force
- `18` — Web Spam
- `19` — Email Spam
- `20` — Blog Spam
- `21` — VPN IP
- `22` — DNS Compromise

See [AbuseIPDB Categories](https://www.abuseipdb.com/categories) for the full list.

### Example Requests

**Using Query Parameters:**
```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report?ip=192.0.2.1&categories=15,18&comment=Brute force attack on SSH"
```

**Using JSON Body:**
```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.1",
    "categories": "15,18",
    "comment": "Multiple failed login attempts detected from this IP"
  }'
```

### Response Format

**Success (HTTP 200):**
```json
{
  "data": {
    "ipAddress": "192.0.2.1",
    "abuseConfidenceScore": 52
  }
}
```

### Error Responses

**Missing Parameters (HTTP 400):**
```
Missing required parameters: ip, categories, comment
```

**API Error (HTTP 500):**
```
Error: AbuseIPDB report failed: 422 Invalid category
```

## Configuration

### Required Environment Variable

- `ABUSEIPDB_API_KEY` — Your AbuseIPDB API key

### Local Development Setup

```bash
func settings add ABUSEIPDB_API_KEY "your-api-key-here"
```

### Azure Production Setup

```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --settings ABUSEIPDB_API_KEY="your-api-key"
```

### Obtaining an API Key

1. Create a free account at https://www.abuseipdb.com/register
2. Navigate to your account page
3. Generate an API key under the API section
4. Free tier includes 1,000 daily checks

## Rate Limits

AbuseIPDB enforces rate limits based on your account tier:

- **Free Tier**: 1,000 checks per day
- **Basic Tier**: 3,000 checks per day
- **Premium Tier**: 100,000 checks per day

The endpoint returns HTTP 500 with an error message if rate limits are exceeded.

## Security Considerations

- API key is stored securely in environment variables
- Never log or expose API keys in error messages
- Reports are public and visible to all AbuseIPDB users
- Only report IPs you have legitimate evidence of abuse for
- False reports may result in account suspension

> [!WARNING]
> Submitting false abuse reports violates AbuseIPDB's Terms of Service and may result in account termination. Only report IPs for which you have concrete evidence of malicious activity.

## Use Cases

### Checking IP Reputation

- Analyze IPs from firewall logs
- Screen IPs before allowing access
- Investigate suspicious activity
- Automated threat intelligence enrichment

### Reporting Malicious IPs

- Report brute-force attacks
- Report spam sources
- Report DDoS participants
- Share threat intelligence with community

## Error Handling

- **HTTP 400** — Missing or invalid parameters
- **HTTP 500** — API errors (authentication, rate limits, service issues)

All API responses return the full AbuseIPDB API response or error message.

## Troubleshooting

### "AbuseIPDB API key not set"

Ensure `ABUSEIPDB_API_KEY` is configured in your environment. For local development, use `func settings add`. For Azure, add to Application Settings.

### "AbuseIPDB check failed: 401"

Your API key is invalid or expired. Generate a new key from your AbuseIPDB account.

### "AbuseIPDB check failed: 429"

Rate limit exceeded. Upgrade your account tier or wait until the daily limit resets.

### "AbuseIPDB report failed: 422"

Invalid category ID or malformed request. Check category IDs against the official list.

## Implementation & Tests

- **Implementation**: `functions/abuseipdb.py`
- **Implementation Documentation**: `docs/implementation/abuseipdb.md`
- **Unit Tests**: `tests/test_abuseipdb.py` (mocked API calls)
- **Endpoint Tests**: `tests/test_abuseipdb_endpoint.py` (HTTP endpoint behavior)
- **Live Tests**: `tests/test_abuseipdb_live.py` (marked with `@pytest.mark.endpoint`)

## Related Resources

- [AbuseIPDB API Documentation](https://docs.abuseipdb.com/)
- [AbuseIPDB Check Endpoint](https://docs.abuseipdb.com/#check-endpoint)
- [AbuseIPDB Report Endpoint](https://docs.abuseipdb.com/#report-endpoint)
- [AbuseIPDB Category List](https://www.abuseipdb.com/categories)
