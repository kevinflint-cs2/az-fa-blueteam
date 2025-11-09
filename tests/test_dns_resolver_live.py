import asyncio
import random
import string

import pytest

from functions.dns_resolver import resolve_domains_async


@pytest.mark.endpoint
def test_live_resolve_example_and_google():
    # Basic live integration: resolve example.com and google.com
    results = asyncio.get_event_loop().run_until_complete(
        resolve_domains_async(["example.com", "google.com"], timeout=5.0, concurrency=10)
    )
    assert isinstance(results, list)
    assert len(results) == 2
    # example.com is expected to be resolvable and unsigned
    ex = results[0]
    assert ex["domain"] == "example.com"
    assert ex["resolvable"] is True
    assert isinstance(ex["ip_addresses"], list)
    assert ex["dnssec"] in ("unsigned", "signed-present", "unknown")


@pytest.mark.endpoint
def test_live_nxdomain_random():
    # Random high-entropy domain should be NXDOMAIN
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    domain = f"{rnd}.example.invalid"
    results = asyncio.get_event_loop().run_until_complete(
        resolve_domains_async([domain], timeout=5.0, concurrency=5)
    )
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is False
    assert r["error"] is not None
    # NXDOMAIN or NoAnswer are acceptable error types depending on resolver
    assert r["error"]["type"] in ("NXDOMAIN", "NoAnswer", "Timeout")
