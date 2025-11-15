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
