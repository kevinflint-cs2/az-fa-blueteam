"""
URLScan.io submission module for Azure Functions.

This module provides functionality to submit URLs to URLScan.io for scanning
and threat analysis.
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


def handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    """
    Handle a URLScan.io submission request.

    This is the main entry point called by function_app.py.

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
