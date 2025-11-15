"""
Unit tests for the urlscan module.

These tests mock all external API calls and validate the module's logic.
"""

import os
from typing import Any
from unittest.mock import patch

import pytest
import requests

from functions import urlscan


@pytest.mark.mock
def test_submit_url_success():
    """Test successful URL submission to URLScan.io."""
    mock_response = {
        "message": "Submission successful",
        "uuid": "abc123-def456-ghi789",
        "result": "https://urlscan.io/result/abc123-def456-ghi789/",
        "api": "https://urlscan.io/api/v1/result/abc123-def456-ghi789/",
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.json.return_value = mock_response

            result = urlscan.submit_url("https://example.com", "public")

            assert result["uuid"] == "abc123-def456-ghi789"
            assert result["message"] == "Submission successful"
            assert "urlscan.io/result" in result["result"]

            # Verify API call was made correctly
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://urlscan.io/api/v1/scan/"
            assert call_args[1]["headers"]["API-Key"] == "test-api-key"
            assert call_args[1]["json"]["url"] == "https://example.com"
            assert call_args[1]["json"]["visibility"] == "public"


@pytest.mark.mock
def test_submit_url_missing_api_key():
    """Test that missing API key raises RuntimeError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="URLSCAN_API_KEY"):
            urlscan.submit_url("https://example.com")


@pytest.mark.mock
def test_submit_url_empty_url():
    """Test that empty URL raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="url parameter cannot be empty"):
            urlscan.submit_url("")


@pytest.mark.mock
def test_submit_url_whitespace_url():
    """Test that whitespace-only URL raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="url parameter cannot be empty"):
            urlscan.submit_url("   ")


@pytest.mark.mock
def test_submit_url_invalid_visibility():
    """Test that invalid visibility value raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="visibility must be one of"):
            urlscan.submit_url("https://example.com", "invalid")


@pytest.mark.mock
def test_submit_url_valid_visibility_options():
    """Test all valid visibility options."""
    mock_response = {
        "message": "Submission successful",
        "uuid": "test-uuid",
        "result": "https://urlscan.io/result/test-uuid/",
        "api": "https://urlscan.io/api/v1/result/test-uuid/",
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.json.return_value = mock_response

            # Test each valid visibility option
            for visibility in ["public", "unlisted", "private"]:
                result = urlscan.submit_url("https://example.com", visibility)
                assert result["uuid"] == "test-uuid"

                # Verify the visibility was passed correctly
                call_args = mock_post.call_args
                assert call_args[1]["json"]["visibility"] == visibility


@pytest.mark.mock
def test_submit_url_api_auth_error():
    """Test handling of authentication errors (401)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "invalid-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = False
            mock_post.return_value.status_code = 401
            mock_post.return_value.text = "Unauthorized"

            with pytest.raises(RuntimeError, match="authentication failed"):
                urlscan.submit_url("https://example.com")


@pytest.mark.mock
def test_submit_url_api_rate_limit():
    """Test handling of rate limit errors (429)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = False
            mock_post.return_value.status_code = 429
            mock_post.return_value.text = "Rate limit exceeded"

            with pytest.raises(RuntimeError, match="rate limit exceeded"):
                urlscan.submit_url("https://example.com")


@pytest.mark.mock
def test_submit_url_api_server_error():
    """Test handling of server errors (500)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = False
            mock_post.return_value.status_code = 500
            mock_post.return_value.text = "Internal Server Error"

            with pytest.raises(RuntimeError, match="500"):
                urlscan.submit_url("https://example.com")


@pytest.mark.mock
def test_submit_url_timeout():
    """Test handling of request timeout."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.Timeout()

            with pytest.raises(RuntimeError, match="timed out"):
                urlscan.submit_url("https://example.com")


@pytest.mark.mock
def test_submit_url_connection_error():
    """Test handling of connection errors."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.side_effect = requests.exceptions.ConnectionError("Network error")

            with pytest.raises(RuntimeError, match="request failed"):
                urlscan.submit_url("https://example.com")


@pytest.mark.mock
def test_handle_request_success():
    """Test handle_request with valid payload."""
    mock_response = {
        "message": "Submission successful",
        "uuid": "test-uuid",
        "result": "https://urlscan.io/result/test-uuid/",
        "api": "https://urlscan.io/api/v1/result/test-uuid/",
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.json.return_value = mock_response

            payload = {"url": "https://example.com", "visibility": "unlisted"}
            result = urlscan.handle_request(payload)

            assert result["status"] == "ok"
            assert result["result"]["uuid"] == "test-uuid"


@pytest.mark.mock
def test_handle_request_missing_url():
    """Test handle_request with missing URL parameter."""
    payload: dict[str, Any] = {}
    with pytest.raises(ValueError, match="missing 'url' parameter"):
        urlscan.handle_request(payload)


@pytest.mark.mock
def test_handle_request_empty_url():
    """Test handle_request with empty URL parameter."""
    payload = {"url": ""}
    with pytest.raises(ValueError, match="missing 'url' parameter"):
        urlscan.handle_request(payload)


@pytest.mark.mock
def test_handle_request_default_visibility():
    """Test handle_request uses 'public' visibility by default."""
    mock_response = {
        "message": "Submission successful",
        "uuid": "test-uuid",
        "result": "https://urlscan.io/result/test-uuid/",
        "api": "https://urlscan.io/api/v1/result/test-uuid/",
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.json.return_value = mock_response

            payload = {"url": "https://example.com"}
            result = urlscan.handle_request(payload)

            assert result["status"] == "ok"

            # Verify default visibility was used
            call_args = mock_post.call_args
            assert call_args[1]["json"]["visibility"] == "public"


@pytest.mark.mock
def test_handle_request_custom_timeout():
    """Test that custom timeout from environment is used."""
    mock_response = {
        "message": "Submission successful",
        "uuid": "test-uuid",
        "result": "https://urlscan.io/result/test-uuid/",
        "api": "https://urlscan.io/api/v1/result/test-uuid/",
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key", "URLSCAN_TIMEOUT": "20"}):
        with patch("requests.post") as mock_post:
            mock_post.return_value.ok = True
            mock_post.return_value.json.return_value = mock_response

            payload = {"url": "https://example.com"}
            urlscan.handle_request(payload)

            # Verify custom timeout was used
            call_args = mock_post.call_args
            assert call_args[1]["timeout"] == 20


# Tests for get_result function
@pytest.mark.mock
def test_get_result_success():
    """Test successful result retrieval from URLScan.io."""
    mock_response = {
        "page": {
            "url": "https://example.com",
            "domain": "example.com",
            "ip": "93.184.216.34",
        },
        "lists": {
            "ips": ["93.184.216.34"],
            "domains": ["example.com"],
        },
        "verdicts": {
            "overall": {
                "score": 0,
                "malicious": False,
            }
        },
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = urlscan.get_result("abc123-def456-ghi789")

            assert result["page"]["domain"] == "example.com"
            assert result["verdicts"]["overall"]["malicious"] is False

            # Verify API call was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "abc123-def456-ghi789" in call_args[0][0]
            assert call_args[1]["headers"]["API-Key"] == "test-api-key"


@pytest.mark.mock
def test_get_result_no_api_key():
    """Test result retrieval works without API key (public scans)."""
    mock_response = {
        "page": {"url": "https://example.com"},
        "lists": {},
        "verdicts": {},
    }

    with patch.dict(os.environ, {}, clear=True):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            result = urlscan.get_result("abc123-def456-ghi789")

            assert result["page"]["url"] == "https://example.com"

            # Verify no API key header was sent
            call_args = mock_get.call_args
            assert "API-Key" not in call_args[1]["headers"]


@pytest.mark.mock
def test_get_result_empty_uuid():
    """Test that empty UUID raises ValueError."""
    with pytest.raises(ValueError, match="uuid parameter cannot be empty"):
        urlscan.get_result("")


@pytest.mark.mock
def test_get_result_whitespace_uuid():
    """Test that whitespace-only UUID raises ValueError."""
    with pytest.raises(ValueError, match="uuid parameter cannot be empty"):
        urlscan.get_result("   ")


@pytest.mark.mock
def test_get_result_invalid_uuid():
    """Test that UUID with invalid characters raises ValueError."""
    with pytest.raises(ValueError, match="invalid characters"):
        urlscan.get_result("abc123$%^&*()")


@pytest.mark.mock
def test_get_result_not_ready():
    """Test handling of scan not ready (404)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 404
            mock_get.return_value.text = "Not Found"

            with pytest.raises(RuntimeError, match="not ready or not found"):
                urlscan.get_result("abc123-def456-ghi789")


@pytest.mark.mock
def test_get_result_deleted():
    """Test handling of deleted scan (410)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 410
            mock_get.return_value.text = "Gone"

            with pytest.raises(RuntimeError, match="deleted"):
                urlscan.get_result("abc123-def456-ghi789")


@pytest.mark.mock
def test_get_result_auth_error():
    """Test handling of authentication errors (401)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "invalid-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 401
            mock_get.return_value.text = "Unauthorized"

            with pytest.raises(RuntimeError, match="authentication failed"):
                urlscan.get_result("abc123-def456-ghi789")


@pytest.mark.mock
def test_get_result_timeout():
    """Test handling of request timeout."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()

            with pytest.raises(RuntimeError, match="timed out"):
                urlscan.get_result("abc123-def456-ghi789")


# Tests for search_scans function
@pytest.mark.mock
def test_search_scans_success():
    """Test successful search on URLScan.io."""
    mock_response = {
        "results": [
            {
                "_id": "scan1",
                "page": {"url": "https://example.com", "domain": "example.com"},
                "task": {"visibility": "public"},
            },
            {
                "_id": "scan2",
                "page": {"url": "https://test.com", "domain": "test.com"},
                "task": {"visibility": "unlisted"},
            },
        ],
        "total": 2,
        "has_more": False,
        "took": 123,
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = mock_response

            result = urlscan.search_scans("domain:example.com", size=10)

            assert len(result["results"]) == 2
            assert result["total"] == 2
            assert result["has_more"] is False

            # Verify API call was made correctly
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["headers"]["API-Key"] == "test-api-key"
            assert call_args[1]["params"]["q"] == "domain:example.com"
            assert call_args[1]["params"]["size"] == 10


@pytest.mark.mock
def test_search_scans_with_pagination():
    """Test search with pagination cursor."""
    mock_response = {
        "results": [{"_id": "scan3"}],
        "total": 100,
        "has_more": True,
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = mock_response

            result = urlscan.search_scans(
                "domain:example.com",
                size=50,
                search_after="12345,abcde"
            )

            assert result["has_more"] is True

            # Verify pagination parameter was sent
            call_args = mock_get.call_args
            assert call_args[1]["params"]["search_after"] == "12345,abcde"


@pytest.mark.mock
def test_search_scans_missing_api_key():
    """Test that missing API key raises RuntimeError."""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(RuntimeError, match="URLSCAN_API_KEY"):
            urlscan.search_scans("domain:example.com")


@pytest.mark.mock
def test_search_scans_empty_query():
    """Test that empty query raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="query parameter cannot be empty"):
            urlscan.search_scans("")


@pytest.mark.mock
def test_search_scans_whitespace_query():
    """Test that whitespace-only query raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="query parameter cannot be empty"):
            urlscan.search_scans("   ")


@pytest.mark.mock
def test_search_scans_invalid_size_too_small():
    """Test that size < 1 raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="size must be between 1 and 10000"):
            urlscan.search_scans("domain:example.com", size=0)


@pytest.mark.mock
def test_search_scans_invalid_size_too_large():
    """Test that size > 10000 raises ValueError."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with pytest.raises(ValueError, match="size must be between 1 and 10000"):
            urlscan.search_scans("domain:example.com", size=10001)


@pytest.mark.mock
def test_search_scans_rate_limit():
    """Test handling of rate limit errors (429)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 429
            mock_get.return_value.text = "Rate limit exceeded"

            with pytest.raises(RuntimeError, match="rate limit exceeded"):
                urlscan.search_scans("domain:example.com")


@pytest.mark.mock
def test_search_scans_auth_error():
    """Test handling of authentication errors (401)."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "invalid-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = False
            mock_get.return_value.status_code = 401
            mock_get.return_value.text = "Unauthorized"

            with pytest.raises(RuntimeError, match="authentication failed"):
                urlscan.search_scans("domain:example.com")


@pytest.mark.mock
def test_search_scans_timeout():
    """Test handling of request timeout."""
    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()

            with pytest.raises(RuntimeError, match="timed out"):
                urlscan.search_scans("domain:example.com")


# Tests for handle_result_request function
@pytest.mark.mock
def test_handle_result_request_success():
    """Test handle_result_request with valid payload."""
    mock_response = {
        "page": {"url": "https://example.com", "domain": "example.com"},
        "lists": {},
        "verdicts": {},
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = mock_response

            payload = {"uuid": "abc123-def456-ghi789"}
            result = urlscan.handle_result_request(payload)

            assert result["status"] == "ok"
            assert result["result"]["page"]["domain"] == "example.com"


@pytest.mark.mock
def test_handle_result_request_missing_uuid():
    """Test handle_result_request with missing UUID parameter."""
    payload: dict[str, Any] = {}
    with pytest.raises(ValueError, match="missing 'uuid' parameter"):
        urlscan.handle_result_request(payload)


@pytest.mark.mock
def test_handle_result_request_empty_uuid():
    """Test handle_result_request with empty UUID parameter."""
    payload = {"uuid": ""}
    with pytest.raises(ValueError, match="missing 'uuid' parameter"):
        urlscan.handle_result_request(payload)


# Tests for handle_search_request function
@pytest.mark.mock
def test_handle_search_request_success():
    """Test handle_search_request with valid payload."""
    mock_response = {
        "results": [{"_id": "scan1", "page": {"domain": "example.com"}}],
        "total": 1,
        "has_more": False,
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = mock_response

            payload = {"q": "domain:example.com", "size": 10}
            result = urlscan.handle_search_request(payload)

            assert result["status"] == "ok"
            assert result["result"]["total"] == 1
            assert len(result["result"]["results"]) == 1


@pytest.mark.mock
def test_handle_search_request_missing_query():
    """Test handle_search_request with missing query parameter."""
    payload: dict[str, Any] = {}
    with pytest.raises(ValueError, match="missing 'q' parameter"):
        urlscan.handle_search_request(payload)


@pytest.mark.mock
def test_handle_search_request_empty_query():
    """Test handle_search_request with empty query parameter."""
    payload = {"q": ""}
    with pytest.raises(ValueError, match="missing 'q' parameter"):
        urlscan.handle_search_request(payload)


@pytest.mark.mock
def test_handle_search_request_default_size():
    """Test handle_search_request uses default size of 100."""
    mock_response = {
        "results": [],
        "total": 0,
        "has_more": False,
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = mock_response

            payload = {"q": "domain:example.com"}
            result = urlscan.handle_search_request(payload)

            assert result["status"] == "ok"

            # Verify default size was used
            call_args = mock_get.call_args
            assert call_args[1]["params"]["size"] == 100


@pytest.mark.mock
def test_handle_search_request_with_pagination():
    """Test handle_search_request with pagination cursor."""
    mock_response = {
        "results": [],
        "total": 100,
        "has_more": True,
    }

    with patch.dict(os.environ, {"URLSCAN_API_KEY": "test-api-key"}):
        with patch("requests.get") as mock_get:
            mock_get.return_value.ok = True
            mock_get.return_value.json.return_value = mock_response

            payload = {"q": "domain:example.com", "size": 50, "search_after": "12345,abcde"}
            result = urlscan.handle_search_request(payload)

            assert result["status"] == "ok"

            # Verify pagination parameter was sent
            call_args = mock_get.call_args
            assert call_args[1]["params"]["search_after"] == "12345,abcde"
