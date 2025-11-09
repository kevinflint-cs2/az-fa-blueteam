import json
import os
import random
import string
import time

import pytest
import requests


# These tests are "live" in the sense they hit the running Functions host endpoint.
# They require you to start the Functions host separately (e.g., `func start`).

BASE_URL = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071")
ENDPOINT = f"{BASE_URL}/api/dns/resolve"


def wait_for_endpoint(url: str, timeout: int = 30) -> None:
    """Poll the endpoint until it responds or timeout.

    Raises AssertionError if the endpoint is not reachable within timeout.
    """
    deadline = time.time() + timeout
    last_exc = None
    while time.time() < deadline:
        try:
            r = requests.options(url, timeout=2)
            # Accept any 2xx/4xx/5xx as the host is up; we only need to confirm it's listening
            if r.status_code >= 200:
                return
        except Exception as exc:
            last_exc = exc
        time.sleep(0.5)
    raise AssertionError(f"Endpoint {url} not reachable within {timeout}s: {last_exc}")


@pytest.mark.endpoint
def test_endpoint_resolve_example_and_google():
    """Call the function endpoint with example.com and google.com and verify response shape.

    Requires the Functions host to be running (`func start`).
    """
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
def test_endpoint_nxdomain_random():
    """Call the function endpoint with a random non-existent domain and expect resolvable=false.

    This verifies the endpoint wiring and that the resolver runs inside the Function host.
    """
    wait_for_endpoint(ENDPOINT, timeout=30)

    rnd = "".join(random.choices(string.ascii_lowercase + string.digits, k=20))
    domain = f"{rnd}.example.invalid"
    payload = {"domains": [domain]}
    r = requests.post(ENDPOINT, json=payload, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) == 1
    item = data[0]
    # resolvable should be false and error populated
    assert item.get("resolvable") is False
    assert item.get("error") is not None
