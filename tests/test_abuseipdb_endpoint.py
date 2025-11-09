import os
import time

import pytest
import requests

BASE_URL = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071")
CHECK_URL = f"{BASE_URL}/api/abuseipdb/check"
REPORT_URL = f"{BASE_URL}/api/abuseipdb/report"


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
def test_abuseipdb_check_missing_param():
    wait_for_endpoint(CHECK_URL, timeout=30)
    r = requests.get(CHECK_URL, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_abuseipdb_report_missing_params():
    wait_for_endpoint(REPORT_URL, timeout=30)
    r = requests.post(REPORT_URL, json={}, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_abuseipdb_check_if_key_present():
    # Optional: only run if ABUSEIPDB_API_KEY is configured in env for the running host
    key = os.getenv("ABUSEIPDB_API_KEY")
    if not key:
        pytest.skip("ABUSEIPDB_API_KEY not set; skipping real check")
    wait_for_endpoint(CHECK_URL, timeout=30)
    r = requests.get(CHECK_URL, params={"ip": "1.1.1.1"}, timeout=10)
    assert r.status_code == 200
