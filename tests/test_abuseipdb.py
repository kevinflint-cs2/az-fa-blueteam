import os
from unittest.mock import patch

import pytest

from functions import abuseipdb

pytestmark = pytest.mark.mock


def test_check_ip_success():
    """Test successful AbuseIPDB check_ip call with mocked response."""
    mock_response = {"data": {"ipAddress": "1.2.3.4", "isWhitelisted": False}}
    with patch("functions.abuseipdb.requests.get") as mock_get:
        mock_get.return_value.ok = True
        mock_get.return_value.json.return_value = mock_response
        os.environ["ABUSEIPDB_API_KEY"] = "dummy"  # pragma: allowlist secret
        result = abuseipdb.check_ip("1.2.3.4")
        assert result == mock_response


def test_check_ip_missing_key():
    """Test check_ip raises if API key is missing."""
    if "ABUSEIPDB_API_KEY" in os.environ:
        del os.environ["ABUSEIPDB_API_KEY"]
    with pytest.raises(RuntimeError):
        abuseipdb.check_ip("1.2.3.4")


def test_check_ip_error():
    """Test check_ip raises on HTTP error."""
    with patch("functions.abuseipdb.requests.get") as mock_get:
        mock_get.return_value.ok = False
        mock_get.return_value.status_code = 400
        mock_get.return_value.text = "Bad Request"
        os.environ["ABUSEIPDB_API_KEY"] = "dummy"  # pragma: allowlist secret
        with pytest.raises(RuntimeError):
            abuseipdb.check_ip("1.2.3.4")


def test_report_ip_success():
    """Test successful AbuseIPDB report_ip call with mocked response."""
    mock_response = {"data": {"ipAddress": "1.2.3.4", "reported": True}}
    with patch("functions.abuseipdb.requests.post") as mock_post:
        mock_post.return_value.ok = True
        mock_post.return_value.json.return_value = mock_response
        os.environ["ABUSEIPDB_API_KEY"] = "dummy"  # pragma: allowlist secret
        result = abuseipdb.report_ip("1.2.3.4", "18", "test comment")
        assert result == mock_response


def test_report_ip_missing_key():
    """Test report_ip raises if API key is missing."""
    if "ABUSEIPDB_API_KEY" in os.environ:
        del os.environ["ABUSEIPDB_API_KEY"]
    with pytest.raises(RuntimeError):
        abuseipdb.report_ip("1.2.3.4", "18", "test comment")


def test_report_ip_error():
    """Test report_ip raises on HTTP error."""
    with patch("functions.abuseipdb.requests.post") as mock_post:
        mock_post.return_value.ok = False
        mock_post.return_value.status_code = 400
        mock_post.return_value.text = "Bad Request"
        os.environ["ABUSEIPDB_API_KEY"] = "dummy"  # pragma: allowlist secret
        with pytest.raises(RuntimeError):
            abuseipdb.report_ip("1.2.3.4", "18", "test comment")
