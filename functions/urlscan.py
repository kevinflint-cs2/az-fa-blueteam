"""
URLScan.io integration module for Azure Functions.

This module provides functionality to submit URLs to URLScan.io for scanning,
retrieve scan results, and search for existing scans.
"""

import os
from typing import Any, cast

import requests


def submit_url(url: str, visibility: str = "public") -> dict[str, Any]:
    """
    Submit a URL to URLScan.io for scanning.

    Args:
        url (str): The URL to scan (must be a valid HTTP/HTTPS URL).
        visibility (str): Scan visibility - "public", "unlisted", or "private".
                         Default is "public".

    Returns:
        dict[str, Any]: The URLScan.io API response containing:
            - uuid: Unique identifier for the scan
            - message: Status message
            - url: Web URL to view results
            - api: API endpoint to retrieve results

    Raises:
        ValueError: If url is empty or visibility is invalid.
        RuntimeError: If API key is missing or the request fails.
    """
    if not url or not url.strip():
        raise ValueError("url parameter cannot be empty")

    # Validate visibility parameter
    valid_visibility = ["public", "unlisted", "private"]
    if visibility not in valid_visibility:
        raise ValueError(f"visibility must be one of {valid_visibility}, got '{visibility}'")

    # Get API key from environment
    api_key = os.getenv("URLSCAN_API_KEY")
    if not api_key:
        raise RuntimeError("URLScan.io API key not set in environment variable 'URLSCAN_API_KEY'.")

    # Prepare request
    api_url = "https://urlscan.io/api/v1/scan/"
    headers = {
        "API-Key": api_key,
        "Content-Type": "application/json",
    }
    payload = {
        "url": url.strip(),
        "visibility": visibility,
    }

    # Get timeout from environment or use default
    timeout = int(os.getenv("URLSCAN_TIMEOUT", "10"))

    # Make API request
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=timeout)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"URLScan.io API request timed out after {timeout} seconds"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"URLScan.io API request failed: {exc}") from exc

    # Check response status
    if not response.ok:
        error_detail = response.text
        if response.status_code == 401:
            raise RuntimeError("URLScan.io API authentication failed. Check API key.")
        elif response.status_code == 429:
            raise RuntimeError("URLScan.io API rate limit exceeded. Try again later.")
        else:
            raise RuntimeError(
                f"URLScan.io API request failed: {response.status_code} {error_detail}"
            )

    # Parse and return response
    return cast(dict[str, Any], response.json())


def get_result(uuid: str) -> dict[str, Any]:
    """
    Retrieve scan results from URLScan.io by UUID.

    Args:
        uuid (str): The scan UUID from submission response.

    Returns:
        dict[str, Any]: The full scan result containing:
            - page: Page metadata (url, domain, ip, country, etc.)
            - lists: Lists of IPs, domains, countries, etc.
            - stats: High-level statistics
            - data: Detailed request/response data
            - verdicts: Security analysis verdicts

    Raises:
        ValueError: If uuid is empty or invalid format.
        RuntimeError: If scan not ready (404), deleted (410), or API errors.
    """
    if not uuid or not uuid.strip():
        raise ValueError("uuid parameter cannot be empty")

    # Basic UUID format validation (should be alphanumeric with hyphens)
    uuid_clean = uuid.strip()
    if not all(c.isalnum() or c == "-" for c in uuid_clean):
        raise ValueError("uuid contains invalid characters")

    # Get API key from environment (optional for result retrieval but recommended)
    api_key = os.getenv("URLSCAN_API_KEY")

    # Prepare request
    api_url = f"https://urlscan.io/api/v1/result/{uuid_clean}/"
    headers = {}
    if api_key:
        headers["API-Key"] = api_key

    # Get timeout from environment or use default
    timeout = int(os.getenv("URLSCAN_TIMEOUT", "10"))

    # Make API request
    try:
        response = requests.get(api_url, headers=headers, timeout=timeout)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"URLScan.io API request timed out after {timeout} seconds"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"URLScan.io API request failed: {exc}") from exc

    # Check response status
    if response.status_code == 404:
        raise RuntimeError(
            "Scan not ready or not found. Please wait and try again."
        )
    elif response.status_code == 410:
        raise RuntimeError("Scan has been deleted.")
    elif response.status_code == 401:
        raise RuntimeError("URLScan.io API authentication failed. Check API key.")
    elif not response.ok:
        error_detail = response.text
        raise RuntimeError(
            f"URLScan.io API request failed: {response.status_code} {error_detail}"
        )

    # Parse and return response
    return cast(dict[str, Any], response.json())


def search_scans(
    query: str, size: int = 100, search_after: str | None = None
) -> dict[str, Any]:
    """
    Search for scans on URLScan.io using ElasticSearch query syntax.

    Args:
        query (str): Search query (e.g., "domain:example.com", "ip:1.2.3.4").
        size (int): Number of results to return (default: 100, max: 10000).
        search_after (str, optional): Pagination cursor from previous result's
                                     'sort' field (comma-separated values).

    Returns:
        dict[str, Any]: Search results containing:
            - results: Array of scan summaries
            - total: Total number of matching scans
            - has_more: Boolean indicating more results available
            - took: Query execution time in milliseconds

    Raises:
        ValueError: If query is empty or size is invalid.
        RuntimeError: If API errors occur (auth, rate limit, etc.).
    """
    if not query or not query.strip():
        raise ValueError("query parameter cannot be empty")

    # Validate size parameter
    if size < 1 or size > 10000:
        raise ValueError("size must be between 1 and 10000")

    # Get API key from environment
    api_key = os.getenv("URLSCAN_API_KEY")
    if not api_key:
        raise RuntimeError(
            "URLScan.io API key not set in environment variable 'URLSCAN_API_KEY'."
        )

    # Prepare request
    api_url = "https://urlscan.io/api/v1/search/"
    headers = {
        "API-Key": api_key,
    }
    params: dict[str, Any] = {
        "q": query.strip(),
        "size": size,
    }
    if search_after:
        params["search_after"] = search_after

    # Get timeout from environment or use default
    timeout = int(os.getenv("URLSCAN_TIMEOUT", "10"))

    # Make API request
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=timeout)
    except requests.exceptions.Timeout as exc:
        raise RuntimeError(
            f"URLScan.io API request timed out after {timeout} seconds"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"URLScan.io API request failed: {exc}") from exc

    # Check response status
    if not response.ok:
        error_detail = response.text
        if response.status_code == 401:
            raise RuntimeError("URLScan.io API authentication failed. Check API key.")
        elif response.status_code == 429:
            raise RuntimeError("URLScan.io API rate limit exceeded. Try again later.")
        else:
            raise RuntimeError(
                f"URLScan.io API request failed: {response.status_code} {error_detail}"
            )

    # Parse and return response
    return cast(dict[str, Any], response.json())


def handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Handle a URLScan.io submission request.

    This is the main entry point called by function_app.py for submissions.

    Args:
        payload (dict[str, Any]): Request payload containing:
            - url (required): The URL to scan
            - visibility (optional): "public", "unlisted", or "private"

    Returns:
        dict[str, Any]: Standardized response with format:
            {
                "status": "ok",
                "result": {
                    "uuid": "...",
                    "message": "...",
                    "url": "...",
                    "api": "..."
                }
            }

    Raises:
        ValueError: If required parameters are missing or invalid.
        RuntimeError: If API errors occur.
    """
    if "url" not in payload or not payload["url"]:
        raise ValueError("missing 'url' parameter")

    url = str(payload["url"])
    visibility = str(payload.get("visibility", "public"))

    # Submit to URLScan.io
    result = submit_url(url, visibility)

    return {"status": "ok", "result": result}


def handle_result_request(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Handle a URLScan.io result retrieval request.

    This is the entry point called by function_app.py for result retrieval.

    Args:
        payload (dict[str, Any]): Request payload containing:
            - uuid (required): The scan UUID

    Returns:
        dict[str, Any]: Standardized response with format:
            {
                "status": "ok",
                "result": { ... full scan result ... }
            }

    Raises:
        ValueError: If required parameters are missing or invalid.
        RuntimeError: If API errors occur (404, 410, etc.).
    """
    if "uuid" not in payload or not payload["uuid"]:
        raise ValueError("missing 'uuid' parameter")

    uuid = str(payload["uuid"])

    # Retrieve result from URLScan.io
    result = get_result(uuid)

    return {"status": "ok", "result": result}


def handle_search_request(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Handle a URLScan.io search request.

    This is the entry point called by function_app.py for searches.

    Args:
        payload (dict[str, Any]): Request payload containing:
            - q (required): Search query
            - size (optional): Number of results (default: 100)
            - search_after (optional): Pagination cursor

    Returns:
        dict[str, Any]: Standardized response with format:
            {
                "status": "ok",
                "result": {
                    "results": [...],
                    "total": ...,
                    "has_more": ...
                }
            }

    Raises:
        ValueError: If required parameters are missing or invalid.
        RuntimeError: If API errors occur.
    """
    if "q" not in payload or not payload["q"]:
        raise ValueError("missing 'q' parameter")

    query = str(payload["q"])
    size = int(payload.get("size", 100))
    search_after = payload.get("search_after")
    if search_after is not None:
        search_after = str(search_after)

    # Search URLScan.io
    result = search_scans(query, size, search_after)

    return {"status": "ok", "result": result}
