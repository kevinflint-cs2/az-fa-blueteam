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
RESULT_URL = f"{BASE_URL}/api/urlscan/result"
SEARCH_URL = f"{BASE_URL}/api/urlscan/search"


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


# Tests for /api/urlscan/result endpoint
@pytest.mark.endpoint
def test_urlscan_result_missing_uuid_param():
    """Test that missing UUID parameter returns 400."""
    wait_for_endpoint(RESULT_URL, timeout=30)
    r = requests.get(RESULT_URL, json={}, timeout=5)
    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"
    assert "uuid" in data["error"]["msg"].lower()


@pytest.mark.endpoint
def test_urlscan_result_empty_uuid():
    """Test that empty UUID parameter returns 400."""
    wait_for_endpoint(RESULT_URL, timeout=30)
    r = requests.get(RESULT_URL, json={"uuid": ""}, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_urlscan_result_invalid_uuid():
    """Test that invalid UUID format returns 400."""
    wait_for_endpoint(RESULT_URL, timeout=30)
    r = requests.get(RESULT_URL, json={"uuid": "invalid$%^&"}, timeout=5)
    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"


@pytest.mark.endpoint
def test_urlscan_result_not_found():
    """Test that non-existent UUID returns 404."""
    wait_for_endpoint(RESULT_URL, timeout=30)
    # Use a valid UUID format that doesn't exist
    r = requests.get(
        RESULT_URL,
        params={"uuid": "00000000-0000-0000-0000-000000000000"},
        timeout=15,
    )
    # Should return 404 for not found or not ready
    assert r.status_code == 404
    data = r.json()
    assert data["status"] == "error"


@pytest.mark.endpoint
def test_urlscan_result_with_query_params():
    """Test result retrieval via query parameters."""
    wait_for_endpoint(RESULT_URL, timeout=30)
    # First submit a URL to get a valid UUID
    submit_r = requests.post(
        SUBMIT_URL,
        json={"url": "https://example.com", "visibility": "unlisted"},
        timeout=15,
    )
    assert submit_r.status_code == 200
    submit_data = submit_r.json()
    uuid = submit_data["result"]["uuid"]

    # Wait a bit for scan to potentially complete
    time.sleep(2)

    # Try to retrieve result (may be 404 if not ready yet, which is expected)
    r = requests.get(RESULT_URL, params={"uuid": uuid}, timeout=15)
    assert r.status_code in [200, 404]  # Either ready or not ready yet

    if r.status_code == 200:
        data = r.json()
        assert data["status"] == "ok"
        assert "result" in data


@pytest.mark.endpoint
def test_urlscan_result_with_json_body():
    """Test result retrieval via JSON body."""
    wait_for_endpoint(RESULT_URL, timeout=30)
    # First submit a URL to get a valid UUID
    submit_r = requests.post(
        SUBMIT_URL,
        json={"url": "https://example.com", "visibility": "unlisted"},
        timeout=15,
    )
    assert submit_r.status_code == 200
    submit_data = submit_r.json()
    uuid = submit_data["result"]["uuid"]

    # Try to retrieve result via JSON body
    r = requests.get(RESULT_URL, json={"uuid": uuid}, timeout=15)
    assert r.status_code in [200, 404]  # Either ready or not ready yet


# Tests for /api/urlscan/search endpoint
@pytest.mark.endpoint
def test_urlscan_search_missing_query_param():
    """Test that missing query parameter returns 400."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(SEARCH_URL, json={}, timeout=5)
    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"
    assert "q" in data["error"]["msg"].lower()


@pytest.mark.endpoint
def test_urlscan_search_empty_query():
    """Test that empty query parameter returns 400."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(SEARCH_URL, json={"q": ""}, timeout=5)
    assert r.status_code == 400


@pytest.mark.endpoint
def test_urlscan_search_invalid_size():
    """Test that invalid size parameter returns 400."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(
        SEARCH_URL,
        json={"q": "domain:example.com", "size": 0},
        timeout=15,
    )
    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"


@pytest.mark.endpoint
def test_urlscan_search_with_query_params():
    """Test search via query parameters."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(
        SEARCH_URL,
        params={"q": "domain:urlscan.io", "size": 5},
        timeout=15,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "results" in data["result"]
    assert "total" in data["result"]
    assert isinstance(data["result"]["results"], list)


@pytest.mark.endpoint
def test_urlscan_search_with_json_body():
    """Test search via JSON body."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(
        SEARCH_URL,
        json={"q": "domain:urlscan.io", "size": 5},
        timeout=15,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "results" in data["result"]


@pytest.mark.endpoint
def test_urlscan_search_default_size():
    """Test that default size is applied when not specified."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(
        SEARCH_URL,
        params={"q": "domain:urlscan.io"},
        timeout=15,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "results" in data["result"]


@pytest.mark.endpoint
def test_urlscan_search_large_size():
    """Test search with large size parameter."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(
        SEARCH_URL,
        params={"q": "domain:urlscan.io", "size": 100},
        timeout=15,
    )

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


@pytest.mark.endpoint
def test_urlscan_search_too_large_size():
    """Test that size > 10000 returns 400."""
    wait_for_endpoint(SEARCH_URL, timeout=30)
    r = requests.get(
        SEARCH_URL,
        params={"q": "domain:urlscan.io", "size": 10001},
        timeout=15,
    )

    assert r.status_code == 400
    data = r.json()
    assert data["status"] == "error"
