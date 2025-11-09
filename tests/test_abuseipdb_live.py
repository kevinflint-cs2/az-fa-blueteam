import pytest
import requests

BASE_URL = "http://localhost:7071/api/abuseipdb"


@pytest.mark.endpoint
def test_live_abuseipdb_check():
    resp = requests.get(f"{BASE_URL}/check", params={"ip": "8.8.8.8"})
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("application/json")
