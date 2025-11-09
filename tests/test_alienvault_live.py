import os

import pytest
import requests

ALIENVAULT_BASE = os.getenv("ALIENVAULT_LIVE_BASE", "http://localhost:7071/api/alienvault")


@pytest.mark.endpoint
def test_live_submit_url():
    resp = requests.post(f"{ALIENVAULT_BASE}/submit_url", json={"url": "http://example.com"})
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")


@pytest.mark.endpoint
def test_live_submit_ip():
    resp = requests.get(f"{ALIENVAULT_BASE}/submit_ip", params={"ip": "8.8.8.8"})
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")


@pytest.mark.endpoint
def test_live_submit_hash():
    resp = requests.get(
        f"{ALIENVAULT_BASE}/submit_hash",
        params={
            "file_hash": "44d88612fea8a8f36de82e1278abb02f",  # pragma: allowlist secret
        },
    )
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")


@pytest.mark.endpoint
def test_live_submit_domain():
    resp = requests.get(f"{ALIENVAULT_BASE}/submit_domain", params={"domain": "example.com"})
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")
