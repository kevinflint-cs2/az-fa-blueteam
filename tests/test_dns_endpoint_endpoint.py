import os
import random
import string
import time

import pytest
import requests

# These tests call the running Functions host endpoint and are marked 'endpoint'.
BASE_URL = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071")
ENDPOINT = f"{BASE_URL}/api/dns/resolve"


def wait_for_endpoint(url: str, timeout: int = 30) -> None:
    deadline = time.time() + timeout
    last_exc = None
    while time.time() < deadline:
        try:
            r = requests.options(url, timeout=2)
            if r.status_code >= 200:
                return
        except Exception as exc:
            last_exc = exc
        time.sleep(0.5)
    raise AssertionError(f"Endpoint {url} not reachable within {timeout}s: {last_exc}")


@pytest.mark.endpoint
def test_endpoint_resolve_example_and_google_http():
    wait_for_endpoint(ENDPOINT, timeout=30)
    payload = {"domains": ["example.com", "google.com"]}
    r = requests.post(ENDPOINT, json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 2
    for item in data:
        assert "domain" in item
        assert "resolvable" in item
        assert "ip_addresses" in item


@pytest.mark.endpoint
def test_endpoint_nxdomain_random_http():
    wait_for_endpoint(ENDPOINT, timeout=30)
    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    domain = f"{rnd}.example.invalid"
    payload = {"domains": [domain]}
    r = requests.post(ENDPOINT, json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item.get("resolvable") is False
    assert item.get("error") is not None
