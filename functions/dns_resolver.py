import asyncio
import json
import os
import time
import random
from typing import Any, Dict, List, Optional, Tuple

import dns.asyncresolver as adns
import dns.exception
import dns.resolver


DEFAULT_TIMEOUT = 3.0
DEFAULT_CONCURRENCY = 50
DEFAULT_RETRIES = 2
DEFAULT_CACHE_TTL = 60
MAX_CNAME_DEPTH = 8


class SimpleTTLCache:
    """A tiny in-memory TTL cache. Not thread-safe but fine for single-process async use."""

    def __init__(self):
        self._data: Dict[Tuple[str, str], Tuple[float, Any]] = {}

    def get(self, name: str, rtype: str):
        key = (name, rtype)
        ent = self._data.get(key)
        if not ent:
            return None
        exp, val = ent
        if time.monotonic() > exp:
            del self._data[key]
            return None
        return val

    def set(self, name: str, rtype: str, value: Any, ttl: Optional[int]):
        key = (name, rtype)
        exp = time.monotonic() + (ttl if ttl is not None else DEFAULT_CACHE_TTL)
        self._data[key] = (exp, value)


_GLOBAL_CACHE = SimpleTTLCache()


def _now_ms() -> int:
    return int(time.monotonic() * 1000)


def _is_transient_error(exc: Exception) -> bool:
    # Consider timeouts and nameserver issues transient; NXDOMAIN/NoAnswer are not
    if isinstance(exc, dns.resolver.NXDOMAIN):
        return False
    if isinstance(exc, dns.resolver.NoAnswer):
        return False
    if isinstance(exc, dns.resolver.NoNameservers):
        return True
    if isinstance(exc, dns.resolver.Timeout) or isinstance(exc, dns.exception.Timeout):
        return True
    # Other DNS exceptions are conservatively transient
    if isinstance(exc, dns.exception.DNSException):
        return True
    return False


async def resolve_domains_async(
    domains: List[str],
    timeout: float = DEFAULT_TIMEOUT,
    per_domain_timeout: Optional[float] = None,
    concurrency: int = DEFAULT_CONCURRENCY,
    nameservers: Optional[List[str]] = None,
    retries: int = DEFAULT_RETRIES,
    cache_ttl_default: int = DEFAULT_CACHE_TTL,
    dnssec_mode: str = "presence",
    metrics_hook: Optional[Any] = None,
    trace_context: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """
    Asynchronously resolve a list of domains and return per-domain result objects.

    See prompts/dns_resolver.md for the full design. This function implements the
    presence-based DNSSEC detection (Level 1) and returns structured errors/metrics/trace info.
    """

    resolver = adns.Resolver()
    resolver.lifetime = timeout
    resolver.timeout = timeout
    if nameservers:
        resolver.nameservers = nameservers

    sem = asyncio.Semaphore(concurrency)

    async def _resolve_one(domain: str) -> Dict[str, Any]:
        start_ms = _now_ms()
        result: Dict[str, Any] = {
            "domain": domain,
            "resolvable": False,
            "ip_addresses": [],
            "name_servers": [],
            "dnssec": "unknown",
            "error": None,
            "metrics": None,
            "trace": None,
        }

        # Simple trace metadata
        span_id = f"span-{random.getrandbits(32):08x}"
        trace = {
            "trace_id": (trace_context or {}).get("trace_id") if trace_context else None,
            "span_id": span_id,
            "parent_span_id": (trace_context or {}).get("parent_span_id") if trace_context else None,
            "nameserver": None,
        }

        attempts = 0
        last_error = None

        async def _do_work() -> None:
            nonlocal attempts, last_error
            name = domain
            # Follow CNAMEs up to max depth
            try:
                for depth in range(MAX_CNAME_DEPTH):
                    try:
                        cached = _GLOBAL_CACHE.get(name, "CNAME")
                        if cached is not None:
                            cname_target = cached
                        else:
                            ans = await resolver.resolve(name, "CNAME")
                            # If we get here and answers exist, follow the first
                            cname_target = ans[0].target.to_text() if ans else None
                            # Cache small TTL if rrset present
                            try:
                                ttl = ans.rrset.ttl
                            except Exception:
                                ttl = cache_ttl_default
                            if cname_target:
                                _GLOBAL_CACHE.set(name, "CNAME", cname_target, ttl)
                        if not cname_target:
                            break
                        # Prevent loops
                        if cname_target == name:
                            raise RuntimeError("CNAME loop detected")
                        name = cname_target
                    except dns.resolver.NoAnswer:
                        # No CNAME, move on
                        break
                    except dns.resolver.NXDOMAIN:
                        raise

                # A and AAAA
                ip_set = []
                for rtype in ("A", "AAAA"):
                    cached = _GLOBAL_CACHE.get(name, rtype)
                    if cached is not None:
                        ips = cached
                    else:
                        try:
                            answers = await resolver.resolve(name, rtype)
                        except Exception as e:
                            answers = None
                            exc = e
                        else:
                            exc = None
                        if answers:
                            ips = [r.to_text() for r in answers]
                            # cache using rrset TTL if available
                            try:
                                ttl = answers.rrset.ttl
                            except Exception:
                                ttl = cache_ttl_default
                            _GLOBAL_CACHE.set(name, rtype, ips, ttl)
                        else:
                            ips = []
                        if exc:
                            raise exc
                    ip_set.extend(ips)

                result["ip_addresses"] = ip_set

                # NS
                try:
                    cached_ns = _GLOBAL_CACHE.get(domain, "NS")
                    if cached_ns is not None:
                        ns_list = cached_ns
                    else:
                        ns_answers = await resolver.resolve(domain, "NS")
                        ns_list = [r.to_text() for r in ns_answers]
                        try:
                            ttl = ns_answers.rrset.ttl
                        except Exception:
                            ttl = cache_ttl_default
                        _GLOBAL_CACHE.set(domain, "NS", ns_list, ttl)
                    result["name_servers"] = ns_list
                except dns.resolver.NoAnswer:
                    result["name_servers"] = []

                # DNSSEC Level 1: presence of RRSIG or DNSKEY
                try:
                    rrsig_present = False
                    try:
                        rrsig_answers = await resolver.resolve(name, "RRSIG")
                        rrsig_present = bool(rrsig_answers)
                    except dns.resolver.NoAnswer:
                        rrsig_present = False

                    # DNSKEY query as fallback for presence
                    dnskey_present = False
                    try:
                        dnskey_answers = await resolver.resolve(domain, "DNSKEY")
                        dnskey_present = bool(dnskey_answers)
                    except dns.resolver.NoAnswer:
                        dnskey_present = False

                    if rrsig_present or dnskey_present:
                        result["dnssec"] = "signed-present"
                    else:
                        result["dnssec"] = "unsigned"
                except Exception:
                    result["dnssec"] = "unknown"

                result["resolvable"] = len(result["ip_addresses"]) > 0

            except Exception as exc:
                last_error = exc
                raise

        # Retry loop
        for attempt in range(retries + 1):
            attempts = attempt + 1
            try:
                async with sem:
                    if per_domain_timeout:
                        await asyncio.wait_for(_do_work(), timeout=per_domain_timeout)
                    else:
                        await _do_work()
                # Success
                last_error = None
                break
            except Exception as exc:
                last_error = exc
                # decide whether to retry
                if not _is_transient_error(exc) or attempt == retries:
                    break
                # exponential backoff with jitter
                backoff = (2 ** attempt) * 0.1
                await asyncio.sleep(backoff + random.random() * backoff)

        end_ms = _now_ms()

        # Fill metrics and trace
        metrics = {
            "duration_ms": end_ms - start_ms,
            "query_count": None,  # could instrument per-query counting if desired
            "retries": attempts - 1,
            "resolved_by_nameserver": (resolver.nameservers[0] if getattr(resolver, "nameservers", None) else None),
        }

        trace["nameserver"] = metrics["resolved_by_nameserver"]

        result["metrics"] = metrics
        result["trace"] = trace

        if last_error is not None:
            # Build structured error
            etype = last_error.__class__.__name__
            result["error"] = {
                "type": etype,
                "message": str(last_error),
                "attempts": attempts,
                "last_nameserver": metrics["resolved_by_nameserver"],
            }
            result["resolvable"] = bool(result["ip_addresses"])

        # Emit metrics hook if present
        try:
            if metrics_hook:
                try:
                    metrics_hook(domain=domain, result=result)
                except Exception:
                    pass
        except Exception:
            pass

        return result

    tasks = [asyncio.create_task(_resolve_one(d)) for d in domains]
    results = await asyncio.gather(*tasks)
    # Ensure results are in same order as input
    return results
