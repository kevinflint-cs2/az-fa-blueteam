## DNS resolver design (async dnspython) — Level 1 DNSSEC, observability, configurable defaults

Purpose
-------
This document defines the design for an asynchronous DNS resolver using dnspython's async APIs. The resolver accepts an array of domains and returns a per-domain object containing whether the domain is resolvable, the A/AAAA IP addresses, NS records, DNSSEC presence (Level 1 detection), and structured observability data (errors, metrics, tracing). All function parameters are configurable via defaults but may be overridden by callers.

Contract
--------
- Input:
  - domains: list/array of domain strings (required)
  - Optional overrides (all with sensible defaults):
    - timeout: float (seconds) — per-query timeout
    - per_domain_timeout: float (seconds) — overall timeout per domain
    - concurrency: int — maximum simultaneous domain workers
    - nameservers: optional list of IP strings to use as resolvers
    - retries: int — number of retry attempts for transient errors
    - cache_ttl_default: int (seconds) — default TTL for cache entries
    - dnssec_mode: str — one of {"presence"} (here we use Level 1 presence detection)

- Output: list/array of objects (one per domain, in the same order as input). Each object has:
  - domain: string
  - resolvable: bool
  - ip_addresses: list[string] (A + AAAA answers combined)
  - name_servers: list[string] (NS records, if available)
  - dnssec: string — "signed-present" | "unsigned" | "unknown" (Level 1 heuristic)
  - error: string | object | null — error information if any (always present as null when no error)
  - metrics: object — simple per-domain metrics (durations, retries, attempts)
  - trace: object — tracing identifiers or metadata (span id, parent id, nameserver used)

Design overview (high level)
----------------------------
1. Validate inputs and deduplicate domains if desired (maintain output order).
2. Create a dnspython async resolver configured with provided nameservers (if any) and per-query timeouts.
3. Use asyncio to create a bounded pool of concurrent per-domain workers (asyncio.Semaphore with `concurrency`).
4. For each domain worker (see per-domain flow below). Aggregate results and return the list in input order.

Per-domain flow
---------------
For each domain, the worker should:

1. Start a per-domain timer (for metrics).
2. Attempt to resolve the final name by following CNAME chains up to a safe max depth (e.g., 8). Track the chain to avoid loops.
3. Query A and AAAA records for the final name (collect all returned IPs). Use the resolver with the configured timeout.
4. Query NS for the domain and collect name servers.
5. DNSSEC Level 1 detection:
   - Query for RRSIG records (for the A/AAAA or NS RRsets) or query DNSKEY for the zone.
   - If RRSIG or DNSKEY is present, set dnssec="signed-present". If not present and queries succeed with no sigs, set dnssec="unsigned".
   - If a DNS query for DNSSEC metadata fails or times out, set dnssec="unknown".
   - This is a presence-based heuristic (Level 1). No cryptographic validation is performed here.
6. Populate ip_addresses and name_servers lists.
7. Set resolvable = True if any A/AAAA records were returned, otherwise False. (The resolver may choose a different rule; this is recommended default.)
8. On exceptions (NXDOMAIN, NoAnswer, SERVFAIL, timeout, NoNameservers, etc.)
   - Do not raise globally; instead populate `error` with structured information and set resolvable=false.
   - For transient errors (SERVFAIL, timeout), honor the configured `retries` with exponential backoff and jitter before final failure.
9. End per-domain timer and fill `metrics` with helpful fields (see Observability below).
10. Return the result object.

Edge cases and handling
-----------------------
- NXDOMAIN: set resolvable=false, error={"type":"NXDOMAIN", "message": ...}.
- NoAnswer (exists but no A/AAAA): resolvable=false, return empty ip_addresses, name_servers if NS query succeeded.
- SERVFAIL/REFUSED/NoNameservers: treated as errors; consider retrying when transient.
- Timeouts: set error={"type":"timeout","details":...} after exhausting retries.
- CNAME chains: follow up to max depth; detect loops and set error if loop detected.
- Wildcard detection (optional): perform a randomized-subdomain lookup and compare answers; if results match, set a flag wildcard=true in `error` or metadata if desired.
- Private/internal IPs: returned as-is in ip_addresses; filtering is left to the caller per requirement.

Observability: errors, metrics, tracing
-------------------------------------
This resolver returns structured observability data with each domain result so callers can log, store, and analyze it.

1. Error field
   - Always include `error` in the per-domain output. If there is no error, set `error: null`.
   - For errors, return either a string message or a structured object. Recommended structured schema:
     {
       "type": "NXDOMAIN" | "SERVFAIL" | "TIMEOUT" | "NO_ANSWER" | "REFUSED" | "OTHER",
       "message": "human-readable summary",
       "code": optional numeric code or resolver-specific code,
       "attempts": number of attempts made,
       "last_nameserver": the nameserver IP used for the last attempt (if applicable)
     }
   - This lets downstream systems ingest errors into databases and perform later reconciliation.

2. Metrics field
   - Include a `metrics` object in the per-domain result with at least:
     {
       "duration_ms": total elapsed ms for the domain lookup,
       "query_count": number of DNS queries made for that domain (A/AAAA/NS/RRSIG/DNSKEY etc.),
       "retries": number of retries attempted,
       "resolved_by_nameserver": IP of the nameserver that returned a successful answer (if applicable)
     }
   - These values can be aggregated by monitoring systems to produce latency histograms and error rates.

3. Trace field
   - Provide lightweight tracing metadata to link the lookup to distributed traces/logs. Example fields:
     {
       "trace_id": optional trace identifier (if available from caller's tracing context),
       "span_id": unique id for this domain lookup, 
       "parent_span_id": parent's span id if provided by caller,
       "nameserver": nameserver IP chosen for the successful query or last attempt
     }
   - If your environment uses OpenTelemetry, the resolver should accept injected trace context (optional) and add span identifiers here.

Metrics/tracing side effects
----------------------------
- The resolver itself should emit structured logs for each domain (info/error) with: domain, resolvable, duration_ms, dnssec, error.type.
- Additionally, the resolver should call a metric hook/callback (if provided) with counters/histograms so the host can push to Prometheus, StatsD, etc. The returned `metrics` object is a convenience snapshot for storage alongside the result.

DNSSEC detection (Level 1) — details
----------------------------------
- Strategy: presence-based detection only. No cryptographic validation.
- Steps:
  - After retrieving A/AAAA/NS answers, also query for RRSIG records for those RRsets. If any RRSIG records are present, mark dnssec="signed-present".
  - If no RRSIGs are present and DNS queries succeed, mark dnssec="unsigned".
  - If the DNSSEC-related query fails or times out, set dnssec="unknown" and include the DNS error in `error`.
- Rationale: Level 1 is fast and provides helpful signal about whether a zone is signed. If stronger guarantees are required later, upgrade to validation or AD-check approaches.

Concurrency, timeouts, and retries
---------------------------------
- Use asyncio with an asyncio.Semaphore sized to `concurrency` to bound simultaneous workers.
- Per-query timeout should be applied to each resolver request (A/AAAA/NS/RRSIG/DNSKEY). Use a conservative default (e.g., 3s).
- Per-domain overall timeout (optional) enforced via asyncio.wait_for around the domain worker.
- Retry policy: for transient failures (SERVFAIL, timeout) retry up to `retries` times using exponential backoff with jitter.

Caching and TTL handling
------------------------
- Use an in-memory TTL cache keyed by (query_name, record_type). When the resolver returns TTL information, respect it for cache expiration; otherwise use `cache_ttl_default`.
- Cache reduces duplicate lookups during the same run and helps performance for repeated domains.

API surface (textual suggestion)
--------------------------------
- Async signature suggestion (text only, no code):
  - resolve_domains_async(domains,
      timeout=3.0,
      per_domain_timeout=None,
      concurrency=50,
      nameservers=None,
      retries=2,
      cache_ttl_default=60,
      dnssec_mode="presence",
      metrics_hook=None,
      trace_context=None)

- Behavior:
  - All parameters have sensible defaults but are overridable by callers.
  - Returns list of per-domain result objects as specified above.
  - Does not raise for per-domain DNS failures; it returns errors in each object's `error` field.

Testing strategy
----------------
- Unit tests: mock dnspython async resolver methods to simulate A/AAAA/NS answers, RRSIG presence, NXDOMAIN, SERVFAIL, timeouts, and CNAME chains.
- Live/integration tests: mark as "live"; test against known signed/unsigned domains and random non-existent domains for NXDOMAIN.
- Performance tests: load test with many domains and verify concurrency and latency under expected limits.

Example result schema (JSON-like)
---------------------------------
{
  "domain": "example.com",
  "resolvable": true,
  "ip_addresses": ["93.184.216.34"],
  "name_servers": ["a.iana-servers.net.", "b.iana-servers.net."],
  "dnssec": "unsigned",
  "error": null,
  "metrics": {"duration_ms": 120, "query_count": 4, "retries": 0, "resolved_by_nameserver": "8.8.8.8"},
  "trace": {"trace_id": "abcd1234", "span_id": "span-1", "parent_span_id": null, "nameserver": "8.8.8.8"}
}

Implementation checklist
------------------------
1. Implement async resolver wrapper using dnspython async API.
2. Implement per-domain worker flow (CNAME follow, A/AAAA, NS, RRSIG) with per-query timeouts.
3. Add retries and exponential backoff for transient errors.
4. Add in-memory TTL cache and honor TTL when provided.
5. Add structured logging and metrics hook invocation.
6. Make DNSSEC detection Level 1 (presence of RRSIG/DNSKEY).
7. Add unit tests with mocked resolver; add live tests for real DNS checks.
8. Provide example usage and integrate into existing project entry points.

Notes
-----
- This design purposely uses a presence-based DNSSEC heuristic (Level 1). If cryptographic validation is needed later, upgrade the design to include trust anchors and dnspython DNSSEC validation or use a validating resolver and check AD flag.
- The `error`, `metrics`, and `trace` fields are designed to be stored downstream for analysis and debugging. Keep them concise to avoid storage bloat.

Status
------
This design document was created to match the requested constraints: async dnspython, Level 1 DNSSEC only, return raw IPs (no filtering), include structured errors/metrics/tracing, and allow all parameters to be modified via defaults.
