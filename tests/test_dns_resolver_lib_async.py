import asyncio
import random
import string

import pytest

from functions.dns_resolver import resolve_domains_async


@pytest.mark.endpoint
def test_lib_async_resolve_example_and_google():
    results = asyncio.get_event_loop().run_until_complete(
        resolve_domains_async(["example.com", "google.com"], timeout=5.0, concurrency=10)
    )
    assert isinstance(results, list)
    assert len(results) == 2


@pytest.mark.endpoint
def test_lib_async_nxdomain_random():
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    domain = f"{rnd}.example.invalid"
    results = asyncio.get_event_loop().run_until_complete(
        resolve_domains_async([domain], timeout=5.0, concurrency=5)
    )
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is False
    assert r["error"] is not None
