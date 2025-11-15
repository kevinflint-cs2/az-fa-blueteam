"""
Live integration tests for URLScan.io submission.

These tests call the actual HTTP endpoint running via Azure Functions host.
They are marked with @pytest.mark.endpoint and require the function host to be running.
"""

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
