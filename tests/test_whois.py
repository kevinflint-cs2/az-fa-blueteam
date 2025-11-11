from unittest.mock import patch

import pytest

from functions import whois

pytestmark = pytest.mark.mock


def test_handle_request_missing_q():
    with pytest.raises(ValueError, match="missing 'q' parameter"):
        whois.handle_request({})


def test_handle_request_detect_ip_and_rdap():
    mock_norm = {"cidr": "1.2.3.0/24"}
    mock_raw = {"network": {"cidr": "1.2.3.0/24"}}
    with patch("functions.whois.fetch_rdap_for_ip") as mock_fetch:
        mock_fetch.return_value = (mock_norm, mock_raw)
        res = whois.handle_request({"q": "1.2.3.4"})
        assert res["status"] == "ok"
        result = res["result"]
        assert result["type"] == "ip"
        assert result["data"]["cidr"] == "1.2.3.0/24"


def test_handle_request_detect_domain_and_whois():
    mock_norm = {"domain_name": "example.com"}
    mock_raw = "raw whois"
    with patch("functions.whois.fetch_whois_for_domain") as mock_fetch:
        mock_fetch.return_value = (mock_norm, mock_raw)
        res = whois.handle_request({"q": "example.com"})
        assert res["status"] == "ok"
        result = res["result"]
        assert result["type"] == "domain"
        assert result["data"]["domain_name"] == "example.com"


def test_reserved_ip_returns_reserved_flag():
    # 192.168.1.1 is private
    res = whois.handle_request({"q": "192.168.1.1"})
    assert res["status"] == "ok"
    result = res["result"]
    assert result["type"] == "ip"
    assert result["data"].get("reserved") is True
