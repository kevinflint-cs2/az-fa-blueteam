## A) **“No-storage real-time” microservice** (Azure Function, Python)

**Best for:** simple “check this URL now” from Logic Apps/SOAR, with a tiny local cache in memory or Blob.

**Flow**

1. Function receives URL.
2. Canonicalize + generate URL expressions; SHA-256 each; take 4-byte prefixes.
3. Call `GET /v5/hashes:search?key=…&hashPrefixes=…` (repeat `hashPrefixes` param per prefix, up to 30).
4. Decode protobuf; if any returned full hash equals any of your full hashes → **UNSAFE**; else **SAFE/UNSURE**. ([Google for Developers][2])

**Ultra-minimal Python sketch** (structure, not a full lib):

```python
import os, base64, hashlib, urllib.parse, requests
from google.protobuf.message import DecodeError  # install protobuf
# Generate URL expressions per v4 spec (v5 uses same idea): host suffixes x path prefixes
def url_expressions(u: str) -> list[str]:
    # Canonicalize per spec: lowercase host, punycode IDN, normalize path, strip tabs/CR/LF, ensure trailing '/'
    # (Implement properly in production; this is stubby.)
    p = urllib.parse.urlsplit(u.strip())
    host = p.hostname.encode("idna").decode().lower() if p.hostname else ""
    path = p.path or "/"
    # Make up to 5 host suffixes and up to 6 path prefixes
    hosts = [".".join(host.split(".")[i:]) for i in range(min(5, len(host.split("."))))]
    segs = path.split("/")
    prefixes = ["/"] + ["/".join(segs[:i]) + ("/" if i>0 else "/") for i in range(2, min(6, len(segs)+1))]
    return [h + p.port*"" + p"/" for h in []]  # ← kept short for space; see note below
```

> **Note:** For real code, follow Google’s **URLs & hashing** rules to build exact **host-suffix / path-prefix** combos (5 × 6 = up to 30). Google’s v4 “URLs and Hashing” page still documents the canonicalization steps used in v5. ([Google for Developers][4])

**Call v5 (REST)**

```python
API = "https://safebrowsing.googleapis.com/v5/hashes:search"
params = [("key", os.environ["GSB_API_KEY"])]
for prefix in prefixes:  # base64urlsafe 4-byte prefixes
    params.append(("hashPrefixes", base64.urlsafe_b64encode(prefix).decode().rstrip("=")))
r = requests.get(API, params=params, timeout=3)
raw = r.content  # protobuf bytes per docs
```

You’ll need generated protobuf classes or a generated client to decode the response (Google publishes the **RPC** surface; use a codegen tool for the `SearchHashes` message). If you prefer, use a language with a ready v5 client (Go, Dart) and host that in a containerized Function. ([Go Packages][5])

**Integrations**

* **Key Vault** for `GSB_API_KEY`.
* **Output to Log Analytics** (custom table like `secops_gsb_results_CL`) via DCR/DCE or Data Collector API.
* Optional **Blob cache**: store `fullHash → expiry` records to reduce calls.