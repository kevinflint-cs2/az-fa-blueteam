# AlienVault OTX Threat Intelligence

This module provides threat intelligence lookups using the AlienVault Open Threat Exchange (OTX) API.

## Endpoints

### 1. URL Submission

Submit a URL for threat intelligence analysis.

**Endpoint:** `POST /api/alienvault/url`

**Parameters:**
- `url` (string, required): The URL to check for threat intelligence

**Example Request (Query Parameter):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/url?url=https://example.com"
```

**Example Request (JSON Body):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

**Example Response:**
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

### 2. IP Address Submission

Submit an IPv4 or IPv6 address for threat intelligence analysis.

**Endpoint:** `POST /api/alienvault/ip`

**Parameters:**
- `ip` (string, required): IPv4 or IPv6 address to check

**Example Request (IPv4):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/ip?ip=8.8.8.8"
```

**Example Request (IPv6):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/ip" \
  -H "Content-Type: application/json" \
  -d '{"ip": "2001:4860:4860::8888"}'
```

**Example Response:**
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
  "asn": "AS15169 Google LLC"
}
```

### 3. File Hash Submission

Submit a file hash (MD5, SHA1, or SHA256) for threat intelligence analysis.

**Endpoint:** `POST /api/alienvault/hash`

**Parameters:**
- `hash` (string, required): File hash (MD5, SHA1, or SHA256)

**Example Request (SHA256):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/hash" \
  -H "Content-Type: application/json" \
  -d '{"hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}'
```

**Example Request (MD5):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/hash?hash=d41d8cd98f00b204e9800998ecf8427e"
```

**Example Response:**
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

### 4. Domain Submission

Submit a domain name for threat intelligence analysis.

**Endpoint:** `POST /api/alienvault/domain`

**Parameters:**
- `domain` (string, required): Domain name to check

**Example Request:**
```bash
curl -X POST "http://localhost:7071/api/alienvault/domain?domain=example.com"
```

**Example Request (JSON Body):**
```bash
curl -X POST "http://localhost:7071/api/alienvault/domain" \
  -H "Content-Type: application/json" \
  -d '{"domain": "google.com"}'
```

**Example Response:**
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

## Response Fields

All endpoints return similar response structures with these common fields:

### Common Fields

- **indicator** (string): The submitted indicator (URL, IP, hash, or domain)
- **sections** (array): Available data sections for this indicator
- **pulse_info** (object): Threat pulse information from OTX community
  - `count` (integer): Number of pulses mentioning this indicator
  - `pulses` (array): List of threat pulses with details
  - `references` (array): External references and IOCs
- **false_positive** (array): Known false positive reports

### IP-Specific Fields

- **reputation** (integer): Reputation score (0 = clean, higher = more suspicious)
- **country_code** (string): Two-letter country code
- **country_name** (string): Full country name
- **city** (string): City name
- **region** (string): State/province/region
- **continent_code** (string): Two-letter continent code
- **latitude** (float): Geographic latitude
- **longitude** (float): Geographic longitude
- **asn** (string): Autonomous System Number and name

### Hash-Specific Fields

- **malware** (object): Malware analysis results (if available)
- **analysis** (object): Static/dynamic analysis results

### URL/Domain-Specific Fields

- **alexa** (string): Alexa ranking information URL
- **whois** (string): WHOIS information URL

## Configuration

### Environment Variable

The API key is retrieved from the `ALIENVAULT_API_KEY` environment variable.

**Local Development:**

Add to `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "ALIENVAULT_API_KEY": "your-api-key-here",
    "AzureWebJobsStorage": "",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
```

**Azure Deployment:**

Set as Application Setting:
```bash
az functionapp config appsettings set \
  --name <function-app-name> \
  --resource-group <resource-group> \
  --settings "ALIENVAULT_API_KEY=your-api-key-here"
```

### Obtaining an API Key

1. Create a free account at https://otx.alienvault.com/
2. Navigate to Settings → API Integration
3. Copy your API key
4. Add to environment configuration

**API Rate Limits:**
- Free tier: 10 requests per second
- No daily request limit
- Unlimited pulses

## Error Handling

### Missing API Key

**Error:** `ALIENVAULT_API_KEY environment variable not set`  
**Status Code:** 500  
**Solution:** Configure the API key in environment variables

### Missing Required Parameter

**Error:** `Missing required parameter: <parameter_name>`  
**Status Code:** 400  
**Solution:** Provide the required parameter (url, ip, hash, or domain)

### Invalid IP Address Format

**Error:** `Error: Invalid IP address format: <ip>`  
**Status Code:** 500  
**Solution:** Verify the IP address is valid IPv4 or IPv6 format

### API Request Failed

**Error:** `AlienVault API request failed: <status_code> <response_text>`  
**Status Code:** 500  
**Solution:** Check API key validity, verify indicator format, check AlienVault status

### Network Error

**Error:** `AlienVault API request failed: <exception_details>`  
**Status Code:** 500  
**Solution:** Check network connectivity, verify firewall rules, check AlienVault service status

## Response Interpretation

### Pulse Count Interpretation

- **pulse_info.count = 0**: No threat intelligence found, likely clean
- **pulse_info.count = 1-5**: Low threat activity, investigate further
- **pulse_info.count > 5**: Moderate to high threat activity, consider blocking
- **pulse_info.count > 20**: Very high threat activity, block immediately

### IP Reputation Score

- **0**: Clean/no reputation data
- **1-3**: Low risk (informational)
- **4-6**: Moderate risk (investigate)
- **7-10**: High risk (likely malicious, consider blocking)

### Malware Analysis

If `malware` field is present with analysis results:
- Check `analysis.info.results` for detection names
- Multiple detections indicate confirmed malware
- Single detection may be false positive (verify with additional sources)

## Best Practices

### When to Use Each Endpoint

1. **URL Endpoint**: Use for suspicious links, phishing URLs, malicious websites
2. **IP Endpoint**: Use for source IPs in logs, firewall events, suspicious connections
3. **Hash Endpoint**: Use for file integrity checks, malware identification, incident response
4. **Domain Endpoint**: Use for DNS queries, email sender domains, C2 detection

### Integration Patterns

1. **SIEM Integration**: Query IPs/domains from security logs for enrichment
2. **Firewall Automation**: Auto-block IPs with high pulse counts
3. **Email Security**: Check URLs and domains in email bodies/headers
4. **Incident Response**: Lookup IOCs during investigation

### Performance Optimization

1. **Caching**: Cache results for frequently queried indicators (TTL: 1 hour)
2. **Batch Processing**: Queue multiple lookups for parallel execution
3. **Rate Limiting**: Respect 10 req/sec limit (use connection pooling)
4. **Timeout Handling**: 10-second timeout prevents indefinite hangs

### Security Considerations

1. **API Key Protection**: Never expose API key in logs or client-side code
2. **Input Validation**: Sanitize all inputs before passing to API
3. **Result Validation**: Verify response structure before processing
4. **False Positives**: Always verify threats with multiple sources

## Troubleshooting

### Issue: No pulse information returned

**Symptom:** `pulse_info.count = 0` for known malicious indicator  
**Possible Causes:**
- Indicator not yet in OTX database
- New/emerging threat
- False negative

**Solutions:**
- Check other threat intelligence sources
- Submit indicator to OTX community
- Wait for community analysis

### Issue: High false positive rate

**Symptom:** Many clean indicators flagged with pulses  
**Possible Causes:**
- Shared infrastructure (CDN, cloud providers)
- Historical compromise (now clean)
- Overly aggressive community reporting

**Solutions:**
- Check `false_positive` field in response
- Verify with reputation score and additional sources
- Review pulse details for context
- Maintain whitelist for known-good infrastructure

### Issue: Rate limit exceeded

**Symptom:** HTTP 429 responses or connection errors  
**Possible Causes:**
- Exceeding 10 requests per second
- Too many parallel requests

**Solutions:**
- Implement request throttling
- Use connection pooling with rate limiting
- Add exponential backoff for retries
- Batch requests efficiently

### Issue: Stale threat intelligence

**Symptom:** Old/outdated threat information  
**Possible Causes:**
- Cached results too long
- Indicator status changed

**Solutions:**
- Reduce cache TTL for critical indicators
- Re-query after incident detection
- Monitor pulse updates via OTX subscriptions

## Notes

- **Free Service**: AlienVault OTX is free for both personal and commercial use
- **Community-Driven**: Threat intelligence is crowdsourced from security community
- **Real-Time Updates**: New pulses are added continuously by contributors
- **Global Coverage**: Threat data from worldwide sources
- **No Authentication Required**: API key only used for rate limit management

## Additional Resources

- **AlienVault OTX Portal**: https://otx.alienvault.com/
- **API Documentation**: https://otx.alienvault.com/api
- **Pulse Explorer**: https://otx.alienvault.com/browse/pulses
- **Community Forum**: https://otx.alienvault.com/forums
- **API Python SDK**: https://github.com/AlienVault-OTX/OTX-Python-SDK

## Related Endpoints

Consider combining AlienVault with these other threat intelligence sources:

- **AbuseIPDB** (`/api/abuseipdb/check`): IP reputation and abuse reports
- **URLScan.io** (`/api/urlscan/submit`): Automated URL scanning and screenshots
- **DNS Resolver** (`/api/dns/resolve`): DNS resolution with DNSSEC validation

## Examples of Threat Detection

### Detecting Phishing URLs

```bash
# Check suspicious email link
curl -X POST "http://localhost:7071/api/alienvault/url" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://paypal-verify.suspicious-domain.com/login"}'

# If pulse_info.count > 0, likely phishing
```

### Identifying Malicious Files

```bash
# Check file hash from quarantine
curl -X POST "http://localhost:7071/api/alienvault/hash" \
  -H "Content-Type: application/json" \
  -d '{"hash": "44d88612fea8a8f36de82e1278abb02f"}'

# Review malware field for detection names
```

### Investigating Command & Control

```bash
# Check domain from DNS logs
curl -X POST "http://localhost:7071/api/alienvault/domain?domain=c2-server.bad-actor.com"

# High pulse count indicates known C2 infrastructure
```

### Analyzing Attack Sources

```bash
# Check IP from failed login attempts
curl -X POST "http://localhost:7071/api/alienvault/ip?ip=203.0.113.42"

# Review pulse_info for attack patterns and campaigns
```
