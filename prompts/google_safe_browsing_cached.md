Got it—here’s a compact **Copilot-ready build brief** for **Option 2A** as its **own Function App**. You can paste this into a repo issue/README and let Copilot scaffold code, tests, and IaC around it.

---

# Build Brief: Azure Function App — Google Safe Browsing v5 (Blob/ADLS cache)

## Goal

Create a dedicated **Azure Function App (Python)** that exposes:

1. **Timer function** to refresh and compact GSB cache into **Blob/ADLS Gen2**.
2. **HTTP function** that performs **low-latency URL checks** using an in-memory prefix→full-hash map (backed by Blob), honoring **positive & negative cache TTLs**, calling `hashes:search` only on misses.

Outputs **auditing telemetry** to **Log Analytics**; cache data lives in **Blob/ADLS** (not LA).

---

## High-Level Architecture

* **Function App**: `wt-func-gsb-cache-<env>` (Python 3.12, Premium EP with pre-warmed instances = 1–2).
* **Storage**: `wtstgsops<env>` container: `gsb-cache/`

  * `prefix_index.parquet` (positive cache; prefix→[(full_hash, threat_type, expires_at)])
  * `negative_cache.parquet` (prefix→negative_expires_at)
* **Functions**

  * `RefreshHashLists` (Timer): pulls `hashLists:batchGet`, compacts Blob parquet files, emits cache health metrics.
  * `CheckUrl` (HTTP POST): validates input, canonicalizes URL, generates host-suffix/path-prefix expressions (≤30), hashes to 4-byte prefixes, checks in-proc map → falls back to `hashes:search` → updates cache → returns verdict JSON.
* **Secrets** in **Key Vault** (Function App settings via KV references): `GSB_API_KEY`, LA DCR endpoint/keys (if using DCR).
* **Observability**:

  * Custom table `secops_gsb_checks_CL` (each request; verdict + latency + cacheHit).
  * Custom table `secops_gsb_cache_health_CL` (timer runs; sizes, entries, lastRefresh, errors).

---

## Public Contract

### HTTP: `POST /api/gsb/check`

**Request**

```json
{ "url": "https://example.test/path?x=1", "source": "sentinel-playbook|manual|other" }
```

**Response**

```json
{
  "url": "https://example.test/path?x=1",
  "verdict": "SAFE|UNSAFE|UNSURE",
  "threats": ["SOCIAL_ENGINEERING","MALWARE"],
  "cacheHit": true,
  "latencyMs": 7,
  "checkedPrefixes": 18,
  "fullHashMatched": true
}
```

**Status codes**: 200 OK, 400 (bad url), 429 (backoff), 500 (unexpected).

### Timer: `RefreshHashLists`

* CRON: `0 */15 * * * *` (every 15 min).
* Artifacts: rewrites `prefix_index.parquet`, `negative_cache.parquet` atomically (tmp → move).
* Emits: `secops_gsb_cache_health_CL` row.

---

## Data Model (Blob & Memory)

* **prefix_index.parquet**: columns

  * `prefix` (BINARY(4)) — 4-byte SHA-256 prefix (raw, not b64)
  * `full_hash` (BINARY(32)) — full SHA-256
  * `threat_type` (STRING) — e.g., SOCIAL_ENGINEERING
  * `expires_at` (TIMESTAMP) — UTC
* **negative_cache.parquet**: columns

  * `prefix` (BINARY(4))
  * `negative_expires_at` (TIMESTAMP)

**In-proc map (on warm start)**

```python
positive: dict[bytes4, list[tuple[bytes32, str, datetime]]]
negative: dict[bytes4, datetime]
```

Background task periodically reloads if Blob `ETag` changes.

---

## URL → Prefix Flow (core)

1. **Canonicalize** URL (lowercase host, IDN punycode, strip tabs/CR/LF, normalize path/query, ensure trailing `/` where required).
2. Generate **host-suffix** × **path-prefix** expressions (cap at 30).
3. SHA-256 each expression → store **4-byte prefixes** and **full 32-byte hashes**.
4. For each prefix:

   * If `positive[prefix]` exists: compare full-hash list; on match → **UNSAFE** (collect threat types).
   * Else if `negative[prefix]` exists and `now < negative_expires_at` → skip server; treat as **SAFE/UNSURE**.
   * Else build batch of ≤30 prefixes → call `GET /v5/hashes:search?key=...&hashPrefixes=...`

     * Parse protobuf; if full hash matches ours → add to positive cache with `expires_at`; otherwise add **negative cache** for the prefix with TTL from response.
5. Verdict: **UNSAFE** if any match, else **SAFE/UNSURE** (choose “UNSURE” only when you had to skip remote due to backoff/limits).

---

## Project Layout (suggested)

```
/src/ai/gsb-cache/
  __init__.py
  canonicalize.py        # URL normalization + expression generation
  hashing.py             # sha256, 4-byte prefix, b64url encode/decode helpers
  cache_loader.py        # Blob parquet load/save, atomic writes, ETag watch
  gsb_client.py          # hashes:search call + protobuf decode
  logic.py               # core check orchestration + TTL handling
  telemetry.py           # Log Analytics writes (checks + health)
  config.py              # env var parsing, KV references, constants
/functions/
  CheckUrl/__init__.py   # HTTP trigger
  RefreshHashLists/__init__.py  # Timer trigger
/protos/
  safebrowsing_v5.proto  # messages used by hashes:search
tests/
  test_canonicalize.py
  test_logic.py
  test_cache_loader.py
infra/
  main.bicep             # FA (Premium), Storage, KV, DCR/DCE, App Settings
  la-dcr.bicep           # secops_gsb_* tables + streams
.devcontainer/
  devcontainer.json
```

---

## Dependencies

* Python: `protobuf`, `httpx` (or `requests`), `azure-identity`, `azure-storage-blob`, `pyarrow` (Parquet), `pandas` (optional for compacting), `tenacity` (retry/backoff).
* Generate protobuf classes from `protos/safebrowsing_v5.proto` (keep pinned).

`requirements.txt` (sketch)

```
protobuf==5.*
httpx==0.27.*
azure-identity==1.*
azure-storage-blob==12.*
pyarrow==17.*
pandas==2.*
tenacity==9.*
```

---

## App Settings (examples)

* `GSB_API_KEY = @Microsoft.KeyVault(SecretUri=...)`
* `GSB_CACHE_CONTAINER = gsb-cache`
* `GSB_PREFIX_INDEX_BLOB = prefix_index.parquet`
* `GSB_NEGATIVE_CACHE_BLOB = negative_cache.parquet`
* `GSB_CACHE_REFRESH_SECONDS = 900`
* `LA_DCR_ENDPOINT`, `LA_DCR_STREAM_ID`, `LA_DCR_KEY` (if using DCR)
* `FUNCTIONS_WORKER_PROCESS_COUNT = 2` (tune)
* `WEBSITE_RUN_FROM_PACKAGE = 1`

---

## Pseudocode (core pieces)

**HTTP Check**

```python
def check_url(url: str, source: str) -> dict:
    u = canonicalize(url)                          # strict per-spec
    exprs = generate_expressions(u)                # ≤30
    hashes = [sha256(e) for e in exprs]
    prefixes = [h[:4] for h in hashes]

    threats = set()
    to_remote = set()

    for p, h in zip(prefixes, hashes):
        if p in positive and any(h == fh for fh, _, exp in positive[p] if now() < exp):
            threats.update(t for fh, t, exp in positive[p] if fh == h and now() < exp)
        elif p in negative and now() < negative[p]:
            continue
        else:
            to_remote.add(p)

    if to_remote:
        resp = gsb_hashes_search(list(to_remote))  # protobuf decode
        # update caches (positive or negative) with TTLs
        update_caches(resp)

        # re-evaluate threats using newly added full hashes
        threats |= evaluate_new_matches(prefixes, hashes)

    verdict = "UNSAFE" if threats else "SAFE"
    return { "url": url, "verdict": verdict, "threats": sorted(threats),
             "cacheHit": len(to_remote)==0, "latencyMs": elapsed_ms, 
             "checkedPrefixes": len(prefixes), "fullHashMatched": bool(threats) }
```

**Timer Refresh**

```python
def refresh_hash_lists():
    lists = gsb_batch_get_hash_lists()        # pull & decode; handle Rice-delta as needed
    positive_df, negative_df = compact_lists_to_parquet(lists)
    write_atomic_blob("prefix_index.parquet", positive_df)
    write_atomic_blob("negative_cache.parquet", negative_df)
    emit_cache_health_metrics()
```

---

## Logging (to Log Analytics)

**`secops_gsb_checks_CL`**

```
TimeGenerated: datetime(now)
URL_s, Verdict_s, ThreatType_s (mv), CacheHit_b, LatencyMs_d, 
CheckedPrefixes_d, RequestsMade_d, FullHashMatched_b, Source_s, 
Failure_s (nullable), Env_s
```

**`secops_gsb_cache_health_CL`**

```
TimeGenerated: datetime(now)
PositiveRows_d, NegativeRows_d, BlobEtag_s, RefreshDurationMs_d, Error_s (nullable)
```

**KQL starters**

```kusto
secops_gsb_checks_CL
| where Verdict_s != "SAFE"
| summarize Hits=count(), URLs=make_set(URL_s, 50) by ThreatType_s, bin(TimeGenerated, 1h)

secops_gsb_cache_health_CL
| summarize any(BlobEtag_s), max(TimeGenerated), avg(PositiveRows_d), avg(NegativeRows_d)
```

---

## IaC (Bicep outline)

* Function App (Premium EP1), Storage, Key Vault, App Insights, Log Analytics, DCR/DCE.
* System-assigned MI; KV access policy/role for secrets.
* App settings wired to KV + DCR values.
* NAT Gateway (optional) for fixed egress.

```bicep
resource fa 'Microsoft.Web/sites@2022-09-01' = {
  name: 'wt-func-gsb-cache-${env}'
  location: location
  kind: 'functionapp'
  properties: {
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.12'
      appSettings: [
        { name: 'GSB_API_KEY', value: kvRef('gsb-api-key') }
        { name: 'GSB_CACHE_CONTAINER', value: 'gsb-cache' }
        // ...
      ]
      preWarmedInstanceCount: 2
    }
    serverFarmId: premiumPlan.id
  }
  identity: { type: 'SystemAssigned' }
}
```

---

## Quality Gates (ask Copilot to write tests)

* Unit tests for:

  * URL canonicalization & expression generation (golden vectors).
  * Prefix/full-hash matching logic (positive & negative TTL).
  * Protobuf parse of `hashes:search` (fixture bytes).
  * Blob parquet round-trip + atomic replace.
* Perf guard: **p95 < 15ms** on warm path (cache hit) for 10–20 prefixes.
* Resilience:

  * Exponential backoff on Google 429/5xx.
  * Circuit breaker to avoid hot loops.
  * Fallback verdict = `UNSURE` when remote is unavailable and no cache.

---

## Security & Compliance

* API key in **Key Vault**, never in code.
* Function App identity with least privilege on Blob container.
* Optional: private endpoints for Storage/KV; NAT for fixed egress.
* Log **no PII**; mask query params; store only necessary URL + verdict.

---

## Developer Experience

* **devcontainer** with Python 3.12, Azure CLI, `func` tools, `protoc`.
* `poe`/`make` tasks:

  * `poe gen-proto` (compile protobuf)
  * `poe run` (func start)
  * `poe test` (pytest + coverage)
  * `poe deploy` (azd/az cli)

---

### What to ask Copilot to do next

* Create all files from the structure above.
* Implement `canonicalize.py` per GSB rules and add tests with known vectors.
* Implement `gsb_client.py` with `hashes:search` GET, protobuf decode, and retries.
* Implement parquet IO + atomic Blob writes.
* Implement `CheckUrl` and `RefreshHashLists` functions with logging to LA.
* Generate Bicep for Function App (Premium EP), KV, Storage, LA, and wire settings.
* Add CI (lint, tests) and a `README.md` with local run + deploy steps.

---

If you want, I can turn this into a repo seed (folders + stubs + tests + Bicep) so you can push and let Copilot fill in the implementations.
