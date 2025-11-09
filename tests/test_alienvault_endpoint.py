import os
import time

import pytest
import requests

BASE_URL = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071")
SUBMIT_URL = f"{BASE_URL}/api/alienvault/submit_url"
SUBMIT_IP = f"{BASE_URL}/api/alienvault/submit_ip"
SUBMIT_HASH = f"{BASE_URL}/api/alienvault/submit_hash"
SUBMIT_DOMAIN = f"{BASE_URL}/api/alienvault/submit_domain"


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
def test_alienvault_submit_url_missing_param():
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(SUBMIT_URL, json={}, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_alienvault_submit_ip_missing_param():
    wait_for_endpoint(SUBMIT_IP, timeout=30)
    r = requests.get(SUBMIT_IP, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_alienvault_submit_hash_missing_param():
    wait_for_endpoint(SUBMIT_HASH, timeout=30)
    r = requests.get(SUBMIT_HASH, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_alienvault_submit_domain_missing_param():
    wait_for_endpoint(SUBMIT_DOMAIN, timeout=30)
    r = requests.get(SUBMIT_DOMAIN, timeout=5)
    assert r.status_code == 400
