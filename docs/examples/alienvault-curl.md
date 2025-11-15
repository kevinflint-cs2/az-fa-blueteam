# Examples: AlienVault OTX (curl)

Examples demonstrating how to call the AlienVault OTX threat intelligence endpoints.

## URL Threat Intelligence

### 1) Check URL using query parameter

```bash
curl -X POST "http://localhost:7071/api/alienvault/url?url=https://example.com"
```

### 2) Check URL using JSON body

```bash
curl -X POST "http://localhost:7071/api/alienvault/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

### 3) Check potentially malicious URL

```bash
curl -X POST "http://localhost:7071/api/alienvault/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://malicious-phishing-site.example"}'
```

### 4) Check URL with path and parameters

```bash
curl -X POST "http://localhost:7071/api/alienvault/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/suspicious/path?param=malicious"}'
```

### 5) Example URL response (clean)

```json
{
  "indicator": "https://example.com",
  "sections": ["general", "url_list"],
  "pulse_info": {
    "count": 0,
    "pulses": [],
    "references": []
  },
  "false_positive": [],
  "alexa": "http://www.alexa.com/siteinfo/example.com"
}
```

### 6) Example URL response (malicious)

```json
{
  "indicator": "http://phishing-example.com",
  "sections": ["general", "url_list"],
  "pulse_info": {
    "count": 5,
    "pulses": [
      {
        "id": "507f1f77bcf86cd799439011",
        "name": "Phishing Campaign Targeting Financial Institutions",
        "description": "Widespread phishing campaign using fake login pages",
        "created": "2025-10-15T09:30:00",
        "modified": "2025-11-14T14:22:00",
        "author_name": "ThreatAnalyst",
        "indicator_type_counts": {
          "URL": 42,
          "domain": 15
        },
        "tags": ["phishing", "financial", "credential-theft"]
      }
    ],
    "references": ["https://example.com/threat-report-123"]
  },
  "false_positive": [],
  "alexa": "http://www.alexa.com/siteinfo/phishing-example.com"
}
```

## IP Address Threat Intelligence

### 7) Check IPv4 address (query parameter)

```bash
curl -X POST "http://localhost:7071/api/alienvault/ip?ip=8.8.8.8"
```

### 8) Check IPv4 address (JSON body)

```bash
curl -X POST "http://localhost:7071/api/alienvault/ip" \
  -H "Content-Type: application/json" \
  -d '{"ip": "8.8.8.8"}'
```

### 9) Check IPv6 address

```bash
curl -X POST "http://localhost:7071/api/alienvault/ip" \
  -H "Content-Type: application/json" \
  -d '{"ip": "2001:4860:4860::8888"}'
```

### 10) Check suspicious IP

```bash
curl -X POST "http://localhost:7071/api/alienvault/ip?ip=203.0.113.42"
```

### 11) Example IPv4 response (clean)

```json
{
  "indicator": "8.8.8.8",
  "sections": ["general", "geo", "reputation", "url_list", "passive_dns", "malware"],
  "pulse_info": {
    "count": 0,
    "pulses": [],
    "references": []
  },
  "false_positive": [],
  "reputation": 0,
  "country_code": "US",
  "country_name": "United States",
  "city": "Mountain View",
  "region": "California",
  "continent_code": "NA",
  "latitude": 37.386,
  "longitude": -122.0838,
  "asn": "AS15169 Google LLC",
  "area_code": 0,
  "postal_code": "94035",
  "dma_code": 807,
  "charset": 0
}
```

### 12) Example IPv4 response (malicious)

```json
{
  "indicator": "203.0.113.42",
  "sections": ["general", "geo", "reputation", "url_list", "passive_dns", "malware"],
  "pulse_info": {
    "count": 15,
    "pulses": [
      {
        "id": "507f191e810c19729de860ea",
        "name": "Botnet C2 Infrastructure - November 2025",
        "description": "Command and control servers for Mirai botnet variant",
        "created": "2025-11-01T08:15:00",
        "modified": "2025-11-14T19:45:00",
        "author_name": "BotnetTracker",
        "indicator_type_counts": {
          "IPv4": 256,
          "domain": 42
        },
        "tags": ["botnet", "c2", "mirai", "ddos"]
      }
    ],
    "references": ["https://example.com/botnet-report"]
  },
  "false_positive": [],
  "reputation": 8,
  "country_code": "CN",
  "country_name": "China",
  "city": "Beijing",
  "region": "Beijing",
  "continent_code": "AS",
  "latitude": 39.9042,
  "longitude": 116.4074,
  "asn": "AS4134 Chinanet"
}
```

## File Hash Threat Intelligence

### 13) Check MD5 hash

```bash
curl -X POST "http://localhost:7071/api/alienvault/hash?hash=d41d8cd98f00b204e9800998ecf8427e"
```

### 14) Check SHA1 hash

```bash
curl -X POST "http://localhost:7071/api/alienvault/hash" \
  -H "Content-Type: application/json" \
  -d '{"hash": "da39a3ee5e6b4b0d3255bfef95601890afd80709"}'
```

### 15) Check SHA256 hash

```bash
curl -X POST "http://localhost:7071/api/alienvault/hash" \
  -H "Content-Type: application/json" \
  -d '{"hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}'
```

### 16) Example hash response (clean)

```json
{
  "indicator": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "sections": ["general", "analysis"],
  "pulse_info": {
    "count": 0,
    "pulses": [],
    "references": []
  },
  "false_positive": [],
  "malware": null,
  "analysis": {
    "info": {
      "results": []
    }
  }
}
```

### 17) Example hash response (malware)

```json
{
  "indicator": "44d88612fea8a8f36de82e1278abb02f",
  "sections": ["general", "analysis"],
  "pulse_info": {
    "count": 8,
    "pulses": [
      {
        "id": "5f8a1b2c3d4e5f6a7b8c9d0e",
        "name": "Ransomware Campaign - October 2025",
        "description": "Widespread ransomware targeting enterprises",
        "created": "2025-10-20T11:30:00",
        "modified": "2025-11-13T16:45:00",
        "author_name": "MalwareAnalysis",
        "indicator_type_counts": {
          "FileHash-SHA256": 128,
          "FileHash-MD5": 128,
          "IPv4": 42
        },
        "tags": ["ransomware", "encryption", "enterprise"]
      }
    ],
    "references": []
  },
  "false_positive": [],
  "malware": {
    "detections": {
      "avast": "Win32:Malware-gen",
      "kaspersky": "Trojan.Win32.Generic",
      "microsoft": "Ransom:Win32/Cryptolocker",
      "symantec": "Trojan.Gen.2"
    },
    "family": "Cryptolocker",
    "type": "Ransomware"
  },
  "analysis": {
    "info": {
      "results": [
        {
          "name": "File encryption detected",
          "severity": "high"
        },
        {
          "name": "Network communication to C2 server",
          "severity": "high"
        }
      ]
    }
  }
}
```

## Domain Threat Intelligence

### 18) Check domain (query parameter)

```bash
curl -X POST "http://localhost:7071/api/alienvault/domain?domain=example.com"
```

### 19) Check domain (JSON body)

```bash
curl -X POST "http://localhost:7071/api/alienvault/domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com"}'
```

### 20) Check suspicious subdomain

```bash
curl -X POST "http://localhost:7071/api/alienvault/domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "phishing.suspicious-domain.com"}'
```

### 21) Example domain response (clean)

```json
{
  "indicator": "google.com",
  "sections": ["general", "geo", "url_list", "passive_dns", "malware", "whois"],
  "pulse_info": {
    "count": 0,
    "pulses": [],
    "references": []
  },
  "false_positive": [],
  "alexa": "http://www.alexa.com/siteinfo/google.com",
  "whois": "http://whois.domaintools.com/google.com"
}
```

### 22) Example domain response (malicious)

```json
{
  "indicator": "malicious-c2.example",
  "sections": ["general", "geo", "url_list", "passive_dns", "malware", "whois"],
  "pulse_info": {
    "count": 12,
    "pulses": [
      {
        "id": "6a7b8c9d0e1f2a3b4c5d6e7f",
        "name": "Command & Control Infrastructure - November",
        "description": "Active C2 domains used by APT group",
        "created": "2025-11-05T14:20:00",
        "modified": "2025-11-14T20:10:00",
        "author_name": "APTTracker",
        "indicator_type_counts": {
          "domain": 86,
          "IPv4": 42
        },
        "tags": ["apt", "c2", "command-control", "malware"]
      }
    ],
    "references": ["https://example.com/apt-report"]
  },
  "false_positive": [],
  "alexa": null,
  "whois": "http://whois.domaintools.com/malicious-c2.example"
}
```

## Error Handling Examples

### 23) Missing required parameter (URL)

```bash
curl -X POST "http://localhost:7071/api/alienvault/url" \
  -H "Content-Type: application/json" \
  -d '{}'
```

Response (HTTP 400):
```
Missing required parameter: url
```

### 24) Missing required parameter (IP)

```bash
curl -X POST "http://localhost:7071/api/alienvault/ip"
```

Response (HTTP 400):
```
Missing required parameter: ip
```

### 25) Invalid IP address format

```bash
curl -X POST "http://localhost:7071/api/alienvault/ip?ip=999.999.999.999"
```

Response (HTTP 500):
```
Error: Invalid IP address format: 999.999.999.999
```

### 26) API key not configured

If `ALIENVAULT_API_KEY` is not set:

Response (HTTP 500):
```
Error: ALIENVAULT_API_KEY environment variable not set
```

### 27) Network timeout/API error

Response (HTTP 500):
```
Error: AlienVault API request failed: HTTPSConnectionPool(host='otx.alienvault.com', port=443): Read timed out.
```

## Interpreting Pulse Counts

### Clean Indicators
```bash
# pulse_info.count = 0 indicates no threat intelligence
curl -X POST "http://localhost:7071/api/alienvault/ip?ip=8.8.8.8"
# Result: Safe to allow
```

### Low Threat Activity
```bash
# pulse_info.count = 1-5 indicates minimal reports
curl -X POST "http://localhost:7071/api/alienvault/domain?domain=some-site.com"
# Result: Investigate further, check pulse details
```

### Moderate Threat Activity
```bash
# pulse_info.count = 6-20 indicates confirmed threat
curl -X POST "http://localhost:7071/api/alienvault/url?url=http://suspicious.com"
# Result: Likely malicious, consider blocking
```

### High Threat Activity
```bash
# pulse_info.count > 20 indicates well-known threat
curl -X POST "http://localhost:7071/api/alienvault/hash?hash=44d88612fea8a8f36de82e1278abb02f"
# Result: Confirmed malicious, block immediately
```

## IP Reputation Score Interpretation

| Score | Risk Level | Action                          |
|-------|------------|---------------------------------|
| 0     | Unknown    | No reputation data available    |
| 1-3   | Low        | Monitor, likely benign          |
| 4-6   | Moderate   | Investigate, check context      |
| 7-8   | High       | Suspicious, consider blocking   |
| 9-10  | Critical   | Malicious, block immediately    |

## Batch Query Example

Check multiple indicators sequentially:

```bash
#!/bin/bash

# Check list of IPs
for ip in 8.8.8.8 1.1.1.1 203.0.113.42; do
  echo "Checking $ip..."
  curl -s "http://localhost:7071/api/alienvault/ip?ip=$ip" | jq '.pulse_info.count'
done

# Check list of domains
for domain in google.com example.com malicious.bad; do
  echo "Checking $domain..."
  curl -s "http://localhost:7071/api/alienvault/domain?domain=$domain" | jq '.pulse_info.count'
done
```

## Integration with jq for Parsing

### Extract pulse count
```bash
curl -s "http://localhost:7071/api/alienvault/ip?ip=8.8.8.8" | jq '.pulse_info.count'
```

### Extract reputation score
```bash
curl -s "http://localhost:7071/api/alienvault/ip?ip=8.8.8.8" | jq '.reputation'
```

### Extract country information
```bash
curl -s "http://localhost:7071/api/alienvault/ip?ip=8.8.8.8" | jq '{country: .country_name, city: .city}'
```

### List all pulse names
```bash
curl -s "http://localhost:7071/api/alienvault/ip?ip=203.0.113.42" | jq '.pulse_info.pulses[].name'
```

### Extract malware detections
```bash
curl -s "http://localhost:7071/api/alienvault/hash?hash=44d88612fea8a8f36de82e1278abb02f" | jq '.malware.detections'
```

## Combining with Other Endpoints

### Cross-reference IP with AbuseIPDB
```bash
# Check AlienVault first
av_count=$(curl -s "http://localhost:7071/api/alienvault/ip?ip=203.0.113.42" | jq '.pulse_info.count')

# If threats found, cross-check with AbuseIPDB
if [ "$av_count" -gt 0 ]; then
  curl "http://localhost:7071/api/abuseipdb/check?ip=203.0.113.42"
fi
```

### Domain to IP resolution and threat check
```bash
# First resolve domain
ips=$(curl -s "http://localhost:7071/api/dns/resolve" \
  -H "Content-Type: application/json" \
  -d '{"domains": ["suspicious-site.com"]}' | jq -r '.[0].ipv4_addresses[]')

# Then check each IP
for ip in $ips; do
  curl "http://localhost:7071/api/alienvault/ip?ip=$ip"
done
```

## Notes

- The Functions host must be running locally for `localhost:7071` examples to work
- The `ALIENVAULT_API_KEY` environment variable must be configured
- For production, replace `http://localhost:7071` with your deployed function URL
- AlienVault OTX is free with rate limit of 10 requests per second
- Pulse information is community-contributed and updated in real-time
- Use `jq` command-line tool for parsing JSON responses

## Best Practices

### URL Checks
- Always check URLs from emails, SMS, or untrusted sources
- Verify shortened URLs before visiting
- Check domains extracted from URL paths

### IP Checks
- Query IPs from firewall logs regularly
- Check source IPs of failed authentication attempts
- Validate IPs before whitelisting

### Hash Checks
- Check file hashes before execution
- Verify downloads against known-good hashes
- Query hashes from quarantined files

### Domain Checks
- Check sender domains from suspicious emails
- Verify DNS query logs for C2 activity
- Monitor newly registered domains in your infrastructure

## Troubleshooting

### No pulses returned for known threat

**Cause**: Indicator not yet in OTX database  
**Solution**: Submit to OTX community, check other threat feeds

### High rate of false positives

**Cause**: Shared infrastructure (CDNs, cloud providers)  
**Solution**: Check `false_positive` field, maintain whitelist

### Rate limit exceeded

**Cause**: More than 10 requests per second  
**Solution**: Implement request throttling, use connection pooling

### Stale threat data

**Cause**: Cached results or old pulse information  
**Solution**: Reduce cache TTL, re-query critical indicators

## References

- **AlienVault OTX Portal**: https://otx.alienvault.com/
- **API Documentation**: https://otx.alienvault.com/api
- **Pulse Explorer**: https://otx.alienvault.com/browse/pulses
- **Category Reference**: https://otx.alienvault.com/browse/global/pulses
- **API Python SDK**: https://github.com/AlienVault-OTX/OTX-Python-SDK
