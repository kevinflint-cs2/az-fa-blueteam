from unittest.mock import patch

import pytest

from functions import alienvault

pytestmark = pytest.mark.mock


# Mock API key and requests.post/get
@pytest.fixture(autouse=True)
def patch_env(monkeypatch):
    monkeypatch.setenv("ALIENVAULT_API_KEY", "testkey")


@patch("functions.alienvault.requests.post")
def test_submit_url_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"result": "ok"}
    result = alienvault.submit_url("http://example.com")
    assert result == {"result": "ok"}


@patch("functions.alienvault.requests.get")
def test_submit_ip_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"result": "ok"}
    result = alienvault.submit_ip("1.2.3.4")
    assert result == {"result": "ok"}


@patch("functions.alienvault.requests.get")
def test_submit_hash_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"result": "ok"}
    result = alienvault.submit_hash("abcd1234")
    assert result == {"result": "ok"}


@patch("functions.alienvault.requests.get")
def test_submit_domain_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"result": "ok"}
    result = alienvault.submit_domain("example.com")
    assert result == {"result": "ok"}


@patch("functions.alienvault.requests.post")
def test_submit_url_error(mock_post):
    mock_post.return_value.status_code = 400
    mock_post.return_value.text = "Bad Request"
    mock_post.return_value.ok = False
    with pytest.raises(RuntimeError):
        alienvault.submit_url("badurl")


@patch("functions.alienvault.requests.get")
def test_submit_ip_error(mock_get):
    mock_get.return_value.status_code = 400
    mock_get.return_value.text = "Bad Request"
    mock_get.return_value.ok = False
    with pytest.raises(RuntimeError):
        alienvault.submit_ip("badip")


@patch("functions.alienvault.requests.get")
def test_submit_hash_error(mock_get):
    mock_get.return_value.status_code = 400
    mock_get.return_value.text = "Bad Request"
    mock_get.return_value.ok = False
    with pytest.raises(RuntimeError):
        alienvault.submit_hash("badhash")


@patch("functions.alienvault.requests.get")
def test_submit_domain_error(mock_get):
    mock_get.return_value.status_code = 400
    mock_get.return_value.text = "Bad Request"
    mock_get.return_value.ok = False
    with pytest.raises(RuntimeError):
        alienvault.submit_domain("baddomain")
