"""
Endpoint tests for the URLScan.io submission function.

These tests verify the HTTP endpoint behavior, including request parsing,
response formatting, and error handling.
"""

import os
import time

import pytest
import requests

BASE_URL = os.getenv("FUNCTION_BASE_URL", "http://localhost:7071")
SUBMIT_URL = f"{BASE_URL}/api/urlscan/submit"


def wait_for_endpoint(url: str, timeout: int = 30) -> None:
    """Wait for the Azure Function endpoint to become available."""
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
def test_urlscan_submit_missing_url_param():
    """Test that missing URL parameter returns 400."""
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(SUBMIT_URL, json={}, timeout=5)
    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"
    assert "url" in data["error"]["msg"].lower()


@pytest.mark.endpoint
def test_urlscan_submit_empty_url():
    """Test that empty URL parameter returns 400."""
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(SUBMIT_URL, json={"url": ""}, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_urlscan_submit_invalid_visibility():
    """Test that invalid visibility parameter returns 400."""
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(
        SUBMIT_URL, json={"url": "https://example.com", "visibility": "invalid"}, timeout=5
    )
    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"
    assert "visibility" in data["error"]["msg"].lower()


@pytest.mark.endpoint
def test_urlscan_submit_with_query_params():
    """Test URL submission via query parameters."""
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(
        SUBMIT_URL,
        params={"url": "https://example.com", "visibility": "unlisted"},
        timeout=15,
    )

    # Should succeed if API key is configured in the function host
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "uuid" in data["result"]
    assert "result" in data["result"]


@pytest.mark.endpoint
def test_urlscan_submit_with_json_body():
    """Test URL submission via JSON body."""
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(
        SUBMIT_URL,
        json={"url": "https://example.com", "visibility": "unlisted"},
        timeout=15,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "uuid" in data["result"]


@pytest.mark.endpoint
def test_urlscan_submit_default_visibility():
    """Test that default visibility is applied when not specified."""
    wait_for_endpoint(SUBMIT_URL, timeout=30)
    r = requests.post(
        SUBMIT_URL,
        json={"url": "https://example.com"},
        timeout=15,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "uuid" in data["result"]
