import os
from typing import Any, Dict
import requests
import ipaddress

BASE_URL = "https://otx.alienvault.com"


def get_api_key() -> str:
    """
    Retrieve the AlienVault API key from the environment.
    Returns:
        str: The API key.
    Raises:
        RuntimeError: If the API key is not set.
    """
    api_key = os.getenv("ALIENVAULT_API_KEY")
    if not api_key:
        raise RuntimeError("AlienVault API key not set in environment variable 'ALIENVAULT_API_KEY'.")
    return api_key


def submit_url(url: str) -> Dict[str, Any]:
    """
    Submit a URL to AlienVault OTX for analysis.
    Args:
        url (str): The URL to submit.
    Returns:
        Dict[str, Any]: The API response as a dictionary.
    Raises:
        RuntimeError: If the request fails.
    """
    api_key = get_api_key()
    endpoint = f"{BASE_URL}/api/v1/indicators/submit_url"
    headers = {"X-OTX-API-KEY": api_key, "Accept": "application/json"}
    data = {"url": url}
    response = requests.post(endpoint, headers=headers, data=data, timeout=10)
    if not response.ok:
        raise RuntimeError(f"AlienVault submit_url failed: {response.status_code} {response.text}")
    return response.json()


def submit_ip(ip: str) -> Dict[str, Any]:
    """
    Query AlienVault OTX for information about an IP address (IPv4 or IPv6).
    Args:
        ip (str): The IP address to query.
    Returns:
        Dict[str, Any]: The API response as a dictionary.
    Raises:
        RuntimeError: If the request fails or IP is invalid.
    """
    api_key = get_api_key()
    try:
        ip_obj = ipaddress.ip_address(ip)
    except ValueError:
        raise RuntimeError("Invalid IP address format.")
    version = "IPv4" if ip_obj.version == 4 else "IPv6"
    endpoint = f"{BASE_URL}/api/v1/indicators/{version}/{ip}/general"
    headers = {"X-OTX-API-KEY": api_key, "Accept": "application/json"}
    response = requests.get(endpoint, headers=headers, timeout=10)
    if not response.ok:
        raise RuntimeError(f"AlienVault submit_ip failed: {response.status_code} {response.text}")
    return response.json()


def submit_hash(file_hash: str) -> Dict[str, Any]:
    """
    Query AlienVault OTX for information about a file hash.
    Args:
        file_hash (str): The file hash to query.
    Returns:
        Dict[str, Any]: The API response as a dictionary.
    Raises:
        RuntimeError: If the request fails.
    """
    api_key = get_api_key()
    endpoint = f"{BASE_URL}/api/v1/indicators/file/{file_hash}/general"
    headers = {"X-OTX-API-KEY": api_key, "Accept": "application/json"}
    response = requests.get(endpoint, headers=headers, timeout=10)
    if not response.ok:
        raise RuntimeError(f"AlienVault submit_hash failed: {response.status_code} {response.text}")
    return response.json()


def submit_domain(domain: str) -> Dict[str, Any]:
    """
    Query AlienVault OTX for information about a domain.
    Args:
        domain (str): The domain to query.
    Returns:
        Dict[str, Any]: The API response as a dictionary.
    Raises:
        RuntimeError: If the request fails.
    """
    api_key = get_api_key()
    endpoint = f"{BASE_URL}/api/v1/indicators/domain/{domain}/general"
    headers = {"X-OTX-API-KEY": api_key, "Accept": "application/json"}
    response = requests.get(endpoint, headers=headers, timeout=10)
    if not response.ok:
        raise RuntimeError(f"AlienVault submit_domain failed: {response.status_code} {response.text}")
    return response.json()
