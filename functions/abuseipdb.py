import os
from typing import Any, Dict
import requests


def check_ip(ip: str) -> Dict[str, Any]:
    """
    Query the AbuseIPDB 'check' endpoint for information about an IP address.

    Args:
        ip (str): The IP address to check.

    Returns:
        Dict[str, Any]: The AbuseIPDB API response as a dictionary.

    Raises:
        RuntimeError: If the API key is missing or the request fails.
    """
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        raise RuntimeError("AbuseIPDB API key not set in environment variable 'ABUSEIPDB_API_KEY'.")
    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": api_key, "Accept": "application/json"}
    params = {"ipAddress": ip, "maxAgeInDays": 90}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if not response.ok:
        raise RuntimeError(f"AbuseIPDB check failed: {response.status_code} {response.text}")
    return response.json()


def report_ip(ip: str, categories: str, comment: str) -> Dict[str, Any]:
    """
    Report an IP address to AbuseIPDB using the 'report' endpoint.

    Args:
        ip (str): The IP address to report.
        categories (str): Comma-separated category IDs (see AbuseIPDB docs).
        comment (str): A comment describing the abuse.

    Returns:
        Dict[str, Any]: The AbuseIPDB API response as a dictionary.

    Raises:
        RuntimeError: If the API key is missing or the request fails.
    """
    api_key = os.getenv("ABUSEIPDB_API_KEY")
    if not api_key:
        raise RuntimeError("AbuseIPDB API key not set in environment variable 'ABUSEIPDB_API_KEY'.")
    url = "https://api.abuseipdb.com/api/v2/report"
    headers = {"Key": api_key, "Accept": "application/json"}
    data = {"ip": ip, "categories": categories, "comment": comment}
    response = requests.post(url, headers=headers, data=data, timeout=10)
    if not response.ok:
        raise RuntimeError(f"AbuseIPDB report failed: {response.status_code} {response.text}")
    return response.json()
