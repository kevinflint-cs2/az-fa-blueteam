# Examples: AbuseIPDB (curl)

Examples demonstrating how to call the AbuseIPDB check and report endpoints.

## Check IP Address Reputation

### 1) Simple check using query parameter

```bash
curl "http://localhost:7071/api/abuseipdb/check?ip=8.8.8.8"
```

### 2) Check using JSON body

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/check" \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'
```

### 3) Check suspicious IP address

```bash
curl "http://localhost:7071/api/abuseipdb/check?ip=198.51.100.42"
```

### 4) Check IPv6 address

```bash
curl "http://localhost:7071/api/abuseipdb/check?ip=2001:4860:4860::8888"
```

### 5) Example success response (clean IP)

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
    "lastReportedAt": null,
    "reports": [],
    "hostnames": ["dns.google"]
  }
}
```

### 6) Example success response (malicious IP)

```json
{
  "data": {
    "ipAddress": "203.0.113.42",
    "isPublic": true,
    "ipVersion": 4,
    "isWhitelisted": false,
    "abuseConfidenceScore": 87,
    "countryCode": "CN",
    "usageType": "Data Center/Web Hosting/Transit",
    "isp": "Example Hosting Ltd",
    "domain": "example-host.com",
    "totalReports": 156,
    "numDistinctUsers": 42,
    "lastReportedAt": "2025-11-14T18:32:15+00:00",
    "reports": [
      {
        "reportedAt": "2025-11-14T18:32:15+00:00",
        "comment": "SSH brute force attack",
        "categories": [15],
        "reporterId": 12345,
        "reporterCountryCode": "US"
      }
    ]
  }
}
```

### 7) Example error response (missing IP)

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/check" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response (HTTP 400):
```
Missing required parameter: ip
```

## Report Malicious IP Address

### 8) Report brute-force attack using query parameters

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report?ip=192.0.2.1&categories=15&comment=Multiple%20failed%20SSH%20login%20attempts"
```

### 9) Report brute-force attack using JSON body

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.1",
    "categories": "15",
    "comment": "Multiple failed SSH login attempts from this IP over the past hour"
  }'
```

### 10) Report multiple categories (DDoS + Port Scan)

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "198.51.100.23",
    "categories": "4,14",
    "comment": "DDoS attack targeting our web servers. Port scanning detected on multiple ports."
  }'
```

### 11) Report web spam

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "203.0.113.100",
    "categories": "18",
    "comment": "Automated spam bot posting advertisements in comment forms"
  }'
```

### 12) Report email spam

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.50",
    "categories": "19",
    "comment": "Spam email relay. Sent unsolicited bulk email to multiple recipients."
  }'
```

### 13) Report SQL injection attempt

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "198.51.100.75",
    "categories": "9",
    "comment": "SQL injection attempts detected in URL parameters: admin=1 OR 1=1--"
  }'
```

### 14) Example report success response

```json
{
  "data": {
    "ipAddress": "192.0.2.1",
    "abuseConfidenceScore": 52
  }
}
```

### 15) Example error response (missing parameters)

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{"ip": "192.0.2.1"}'
```

Response (HTTP 400):
```
Missing required parameters: ip, categories, comment
```

### 16) Example error response (invalid category)

```bash
curl -X POST "http://localhost:7071/api/abuseipdb/report" \
  -H "Content-Type: application/json" \
  -d '{
    "ip": "192.0.2.1",
    "categories": "999",
    "comment": "Test report"
  }'
```

Response (HTTP 500):
```
Error: AbuseIPDB report failed: 422 Invalid category
```

## Common Category IDs Reference

| ID  | Category Name       | Description                           |
|-----|---------------------|---------------------------------------|
| 3   | Fraud Orders        | Fraudulent orders                     |
| 4   | DDoS Attack         | Distributed Denial of Service         |
| 9   | Hacking             | Compromised server or system          |
| 10  | Spam                | Generic spam                          |
| 14  | Port Scan           | Port scanning/probing                 |
| 15  | Brute-Force         | Brute-force login attempts            |
| 18  | Web Spam            | Comment/forum spam                    |
| 19  | Email Spam          | Unsolicited bulk email                |
| 20  | Blog Spam           | Blog comment spam                     |
| 21  | VPN IP              | VPN exit node                         |
| 22  | DNS Compromise      | DNS poisoning/manipulation            |

Full list: https://www.abuseipdb.com/categories

## Interpreting Abuse Confidence Score

- **0-25**: Low risk (likely legitimate traffic)
- **26-50**: Moderate risk (some reports, investigate)
- **51-75**: High risk (multiple reports, likely malicious)
- **76-100**: Very high risk (confirmed malicious, block recommended)

## Best Practices

### When Checking IPs

1. **Check before blocking**: Verify reputation before implementing firewall rules
2. **Batch processing**: Check multiple IPs from logs in batch for efficiency
3. **Cache results**: Cache responses for a reasonable time to avoid rate limits
4. **Whitelist awareness**: Note whitelisted IPs (CDNs, legitimate services)

### When Reporting IPs

1. **Provide context**: Include detailed comments with timestamps and log excerpts
2. **Use correct categories**: Select the most specific category that applies
3. **Verify evidence**: Only report IPs with concrete evidence of abuse
4. **Include multiple categories**: If applicable (e.g., brute-force + port scan)
5. **Don't over-report**: Wait for pattern to emerge before reporting

## Notes

- The Functions host must be running locally for `localhost:7071` examples to work
- The `ABUSEIPDB_API_KEY` environment variable must be configured
- For production, replace `http://localhost:7071` with your deployed function URL
- Free tier accounts are limited to 1,000 checks per day
- Reports are permanent and public to all AbuseIPDB users
- Maximum report age is 90 days (use `maxAgeInDays` parameter to customize)

## Rate Limit Tips

- Cache check results to minimize API calls
- Use batch operations when available
- Upgrade account tier for higher limits
- Monitor daily usage to avoid unexpected service disruption
- Implement exponential backoff for rate limit errors

## Security Reminders

> [!WARNING]
> - Never include sensitive data (passwords, tokens, PII) in report comments
> - Verify IP addresses before reporting to avoid false positives
> - Be aware that reports are publicly visible
> - False reporting may result in account suspension
