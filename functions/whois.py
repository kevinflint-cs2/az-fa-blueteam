from __future__ import annotations

import ipaddress
import logging
import os
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)


_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}


def _now_ts() -> float:
    return datetime.now(UTC).timestamp()


def _cache_get(key: str, ttl: int) -> dict[str, Any] | None:
    entry = _CACHE.get(key)
    if not entry:
        return None
    ts, value = entry
    if _now_ts() - ts > ttl:
        del _CACHE[key]
        return None
    return value


def _cache_set(key: str, value: dict[str, Any]) -> None:
    _CACHE[key] = (_now_ts(), value)


def detect_type(q: str) -> str | None:
    """Return 'ip' or 'domain' or None if indeterminate."""
    q = q.strip()
    try:
        ipaddress.ip_address(q)
        return "ip"
    except Exception:
        pass

    # Minimal domain validation: contains a dot and no spaces
    if " " in q:
        return None
    if "." in q:
        return "domain"
    return None


def handle_request(payload: dict[str, Any]) -> dict[str, Any]:
    """Main entrypoint called by function_app.

    payload must contain 'q'. Optional keys: source, raw, timeout
    """
    if "q" not in payload or not payload["q"]:
        raise ValueError("missing 'q' parameter")

    q = str(payload["q"]).strip()
    source_pref = payload.get("source", "auto")
    raw_flag = bool(payload.get("raw", False))
    timeout = int(payload.get("timeout", int(os.getenv("WHOIS_MAX_TIMEOUT", "10"))))

    detected = detect_type(q)
    if not detected:
        raise ValueError("query must be a valid IP or domain")

    cache_key = f"whois:{q}:{source_pref}:{raw_flag}"
    cached = _cache_get(cache_key, int(os.getenv("WHOIS_CACHE_TTL", "86400")))
    if cached:
        return {"status": "ok", "result": cached}

    fetched_at = datetime.now(UTC).isoformat()
    result: dict[str, Any] = {
        "query": q,
        "type": detected,
        "source": None,
        "fetched_at": fetched_at,
        "data": {},
    }

    try:
        if detected == "ip":
            # private/reserved handling
            ip_obj = ipaddress.ip_address(q)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast or ip_obj.is_reserved:
                result["source"] = "local"
                result["data"] = {"reserved": True}
                _cache_set(cache_key, result)
                return {"status": "ok", "result": result}

            # fetch RDAP for IP
            norm_ip, raw_rdap = fetch_rdap_for_ip(q, timeout=timeout)
            result["source"] = "rdap"
            result["data"] = norm_ip
            if raw_flag:
                result["raw"] = raw_rdap
        else:
            # domain
            norm_domain, raw_whois = fetch_whois_for_domain(q, timeout=timeout)
            # determine best source
            result["source"] = "whois"
            result["data"] = norm_domain
            if raw_flag:
                result["raw"] = raw_whois

    except Exception:
        logger.exception("whois lookup failed")
        # bubble up as generic exception for function_app to map
        raise

    _cache_set(cache_key, result)
    return {"status": "ok", "result": result}


def fetch_rdap_for_ip(ip: str, timeout: int = 10) -> tuple[dict[str, Any], dict[str, Any]]:
    """Perform RDAP lookup for an IP and return (normalized, raw_json).

    Imports ipwhois lazily so module import doesn't fail when package missing.
    """
    try:
        from ipwhois import IPWhois
    except Exception as exc:  # pragma: no cover - external lib behavior
        raise RuntimeError("ipwhois library not available") from exc

    obj = IPWhois(ip)
    raw = obj.lookup_rdap(asn_methods=["whois"])

    net = raw.get("network", {}) if isinstance(raw, dict) else {}
    norm: dict[str, Any] = {
        "cidr": net.get("cidr") if net else None,
        "inetnum_start": net.get("startAddress") if net else None,
        "inetnum_end": net.get("endAddress") if net else None,
        "netname": net.get("name") if net else None,
        "handle": net.get("handle") if net else None,
        "country": net.get("country") if net else None,
        "org_name": None,
        "org_handle": None,
        "status_list": net.get("status", []) if net else [],
        "abuse_emails": [],
    }

    # extract org/name
    entities = raw.get("objects", {}) if isinstance(raw, dict) else {}
    # try to find org object
    for obj_key, obj_val in entities.items() if isinstance(entities, dict) else []:
        if not isinstance(obj_val, dict):
            continue
        v = obj_val.get("contact", obj_val)
        roles = obj_val.get("roles", [])
        if "registrant" in roles or "registrant" in obj_key.lower() or "org" in roles:
            norm["org_name"] = v.get("name") or v.get("organization")
            norm["org_handle"] = obj_key
        # collect abuse emails from v
        emails = []
        for e in v.get("emails", []) if isinstance(v.get("emails", []), list) else []:
            emails.append(e)
        if emails:
            norm["abuse_emails"].extend(emails)

    return norm, raw


def fetch_whois_for_domain(domain: str, timeout: int = 10) -> tuple[dict[str, Any], str]:
    """Fetch WHOIS for a domain and return (normalized, raw_text).

    Imports `whois` lazily.
    """
    try:
        import whois as whois_lib
    except Exception as exc:  # pragma: no cover - external lib behavior
        raise RuntimeError("whois library not available") from exc

    w = whois_lib.whois(domain)
    raw_text = str(w)
    if hasattr(w, "domain_name"):
        dn = w.domain_name[0] if isinstance(w.domain_name, (list, tuple)) else w.domain_name
    else:
        dn = domain

    norm: dict[str, Any] = {
        "domain_name": dn,
        "registrar": getattr(w, "registrar", None),
        "created_on": _to_iso(getattr(w, "creation_date", None)),
        "updated_on": _to_iso(getattr(w, "updated_date", None)),
        "expires_on": _to_iso(getattr(w, "expiration_date", None)),
        "nameservers": list(getattr(w, "name_servers", []) or []),
        "emails": list(getattr(w, "emails", []) or []),
    }
    return norm, raw_text


def _to_iso(val: Any) -> str | None:
    if not val:
        return None
    # whois lib may return list or datetime
    if isinstance(val, (list, tuple)):
        val = val[0]
    # Prefer datetime objects for reliable conversion
    if isinstance(val, datetime):
        try:
            return val.astimezone(UTC).isoformat()
        except Exception:
            return None

    # Fallback: try parsing a date/time string
    try:
        return datetime.fromisoformat(str(val)).astimezone(UTC).isoformat()
    except Exception:
        return None
