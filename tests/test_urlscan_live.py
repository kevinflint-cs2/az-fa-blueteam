"""
Live integration tests for URLScan.io endpoints.

These tests call the actual HTTP endpoints running via Azure Functions host.
They are marked with @pytest.mark.endpoint and require the function host to be running
with a valid URLSCAN_API_KEY configured.
"""

import time

import pytest
import requests

BASE_URL = "http://localhost:7071/api/urlscan"


@pytest.mark.endpoint
def test_live_urlscan_submit():
    """Test live URLScan.io submission via HTTP endpoint."""
    resp = requests.post(
        f"{BASE_URL}/submit",
        json={"url": "https://example.com", "visibility": "unlisted"},
        timeout=15,
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")

    data = resp.json()
    assert data["status"] == "ok"
    assert "uuid" in data["result"]
    assert "urlscan.io" in data["result"]["result"]


@pytest.mark.endpoint
def test_live_urlscan_result():
    """Test live URLScan.io result retrieval via HTTP endpoint."""
    # First submit a URL to get a valid UUID
    submit_resp = requests.post(
        f"{BASE_URL}/submit",
        json={"url": "https://urlscan.io", "visibility": "unlisted"},
        timeout=15,
    )
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()
    uuid = submit_data["result"]["uuid"]

    # Wait for scan to complete (URLScan.io typically takes 10-30 seconds)
    max_attempts = 12
    attempt = 0
    while attempt < max_attempts:
        time.sleep(5)
        attempt += 1

        result_resp = requests.get(
            f"{BASE_URL}/result",
            params={"uuid": uuid},
            timeout=15,
        )

        if result_resp.status_code == 200:
            # Scan completed successfully
            data = result_resp.json()
            assert data["status"] == "ok"
            assert "page" in data["result"]
            assert "lists" in data["result"]
            assert "verdicts" in data["result"]
            print(f"Scan completed after {attempt * 5} seconds")
            return

        elif result_resp.status_code == 404:
            # Scan not ready yet, continue polling
            print(f"Attempt {attempt}: Scan not ready, waiting...")
            continue

        else:
            # Unexpected status code
            pytest.fail(f"Unexpected status code: {result_resp.status_code}")

    pytest.fail("Scan did not complete within timeout period")


@pytest.mark.endpoint
def test_live_urlscan_result_not_found():
    """Test URLScan.io result retrieval with non-existent UUID."""
    resp = requests.get(
        f"{BASE_URL}/result",
        params={"uuid": "00000000-0000-0000-0000-000000000000"},
        timeout=15,
    )
    # Should return 404 for non-existent scan
    assert resp.status_code == 404
    data = resp.json()
    assert data["status"] == "error"


@pytest.mark.endpoint
def test_live_urlscan_search():
    """Test live URLScan.io search via HTTP endpoint."""
    resp = requests.get(
        f"{BASE_URL}/search",
        params={"q": "domain:urlscan.io", "size": 5},
        timeout=15,
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")

    data = resp.json()
    assert data["status"] == "ok"
    assert "results" in data["result"]
    assert "total" in data["result"]
    assert isinstance(data["result"]["results"], list)
    # URLscan.io domain should have many scans
    assert data["result"]["total"] > 0


@pytest.mark.endpoint
def test_live_urlscan_search_no_results():
    """Test URLScan.io search with query that returns no results."""
    # Use a very specific query unlikely to match anything
    resp = requests.get(
        f"{BASE_URL}/search",
        params={"q": "domain:thisisaveryrandomdomainthatdoesnotexist123456789.com", "size": 5},
        timeout=15,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "results" in data["result"]
    # May have 0 results
    assert isinstance(data["result"]["results"], list)


@pytest.mark.endpoint
def test_live_urlscan_search_with_size():
    """Test URLScan.io search with custom size parameter."""
    resp = requests.get(
        f"{BASE_URL}/search",
        params={"q": "domain:example.com", "size": 10},
        timeout=15,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "results" in data["result"]
    # Should return at most 10 results
    assert len(data["result"]["results"]) <= 10


@pytest.mark.endpoint
def test_live_urlscan_complete_workflow():
    """Test complete workflow: submit, wait, retrieve result, search."""
    # Step 1: Submit a URL (use urlscan.io itself as it's always allowed)
    submit_resp = requests.post(
        f"{BASE_URL}/submit",
        json={"url": "https://urlscan.io", "visibility": "unlisted"},
        timeout=15,
    )
    assert submit_resp.status_code == 200
    submit_data = submit_resp.json()
    uuid = submit_data["result"]["uuid"]
    print(f"Submitted scan with UUID: {uuid}")

    # Step 2: Search for recent urlscan.io scans
    search_resp = requests.get(
        f"{BASE_URL}/search",
        params={"q": "domain:urlscan.io", "size": 10},
        timeout=15,
    )
    assert search_resp.status_code == 200
    search_data = search_resp.json()
    assert search_data["status"] == "ok"
    assert len(search_data["result"]["results"]) > 0
    print(f"Found {len(search_data['result']['results'])} urlscan.io scans")

    # Step 3: Try to retrieve result (may not be ready yet, which is OK)
    result_resp = requests.get(
        f"{BASE_URL}/result",
        params={"uuid": uuid},
        timeout=15,
    )
    # Either 200 (ready) or 404 (not ready) are both acceptable
    assert result_resp.status_code in [200, 404]
    print(f"Result retrieval status: {result_resp.status_code}")
