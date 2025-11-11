import json
import os

import azure.functions as func

from functions import whois as whois_module
from functions.abuseipdb import check_ip, report_ip
from functions.alienvault import submit_domain, submit_hash, submit_ip, submit_url
from functions.dns_resolver import resolve_domains_async

app = func.FunctionApp()


# AlienVault: submit_url
@app.route(route="alienvault/submit_url", auth_level=func.AuthLevel.FUNCTION)
def alienvault_submit_url(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for submitting a URL to AlienVault OTX.
    Expects 'url' as a query or JSON parameter.
    """
    url = req.params.get("url")
    if not url:
        try:
            req_body = req.get_json()
        except ValueError:
            url = None
        else:
            url = req_body.get("url")
    if not url:
        return func.HttpResponse("Missing required parameter: url", status_code=400)
    try:
        result = submit_url(url)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


# AlienVault: submit_ip
@app.route(route="alienvault/submit_ip", auth_level=func.AuthLevel.FUNCTION)
def alienvault_submit_ip(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for submitting an IP to AlienVault OTX.
    Expects 'ip' as a query or JSON parameter.
    """
    ip = req.params.get("ip")
    if not ip:
        try:
            req_body = req.get_json()
        except ValueError:
            ip = None
        else:
            ip = req_body.get("ip")
    if not ip:
        return func.HttpResponse("Missing required parameter: ip", status_code=400)
    try:
        result = submit_ip(ip)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


# AlienVault: submit_hash
@app.route(route="alienvault/submit_hash", auth_level=func.AuthLevel.FUNCTION)
def alienvault_submit_hash(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for submitting a file hash to AlienVault OTX.
    Expects 'file_hash' as a query or JSON parameter.
    """
    file_hash = req.params.get("file_hash")
    if not file_hash:
        try:
            req_body = req.get_json()
        except ValueError:
            file_hash = None
        else:
            file_hash = req_body.get("file_hash")
    if not file_hash:
        return func.HttpResponse("Missing required parameter: file_hash", status_code=400)
    try:
        result = submit_hash(file_hash)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


# AlienVault: submit_domain
@app.route(route="alienvault/submit_domain", auth_level=func.AuthLevel.FUNCTION)
def alienvault_submit_domain(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for submitting a domain to AlienVault OTX.
    Expects 'domain' as a query or JSON parameter.
    """
    domain = req.params.get("domain")
    if not domain:
        try:
            req_body = req.get_json()
        except ValueError:
            domain = None
        else:
            domain = req_body.get("domain")
    if not domain:
        return func.HttpResponse("Missing required parameter: domain", status_code=400)
    try:
        result = submit_domain(domain)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


# AbuseIPDB: check
@app.route(route="abuseipdb/check", auth_level=func.AuthLevel.FUNCTION)
def abuseipdb_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for checking an IP with AbuseIPDB.
    Expects 'ip' as a query or JSON parameter.
    """
    ip = req.params.get("ip")
    if not ip:
        try:
            req_body = req.get_json()
        except ValueError:
            ip = None
        else:
            ip = req_body.get("ip")
    if not ip:
        return func.HttpResponse("Missing required parameter: ip", status_code=400)
    try:
        result = check_ip(ip)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


# AbuseIPDB: report
@app.route(route="abuseipdb/report", auth_level=func.AuthLevel.FUNCTION)
def abuseipdb_report(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for reporting an IP to AbuseIPDB.
    Expects 'ip', 'categories', and 'comment' as parameters.
    """
    ip = req.params.get("ip")
    categories = req.params.get("categories")
    comment = req.params.get("comment")
    if not ip or not categories or not comment:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        ip = ip or req_body.get("ip")
        categories = categories or req_body.get("categories")
        comment = comment or req_body.get("comment")
    if not ip or not categories or not comment:
        return func.HttpResponse(
            "Missing required parameters: ip, categories, comment", status_code=400
        )
    try:
        result = report_ip(ip, categories, comment)
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)
    return func.HttpResponse(str(result), mimetype="application/json")


# DNS: resolve
@app.route(route="dns/resolve", auth_level=func.AuthLevel.FUNCTION)
async def dns_resolve(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for resolving multiple domains.
    Accepts query param `domains` (comma-separated) or JSON body { "domains": [ ... ] }.
    """
    domains_param = req.params.get("domains")
    domains = None
    if domains_param:
        # allow comma-separated list
        domains = [d.strip() for d in domains_param.split(",") if d.strip()]
    else:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        domains = req_body.get("domains")

    if not domains or not isinstance(domains, list):
        return func.HttpResponse("Missing required parameter: domains (array)", status_code=400)

    # Read defaults from environment (optional overrides)
    timeout = float(os.getenv("DNS_TIMEOUT", "3.0"))
    per_domain_timeout_str = os.getenv("DNS_PER_DOMAIN_TIMEOUT")
    per_domain_timeout: float | None = (
        float(per_domain_timeout_str) if per_domain_timeout_str else None
    )
    concurrency = int(os.getenv("DNS_CONCURRENCY", "50"))
    retries = int(os.getenv("DNS_RETRIES", "2"))
    nameservers_str = os.getenv("DNS_NAMESERVERS")
    nameservers: list[str] | None = None
    if nameservers_str:
        nameservers = [ns.strip() for ns in nameservers_str.split(",") if ns.strip()]

    try:
        result = await resolve_domains_async(
            domains,
            timeout=timeout,
            per_domain_timeout=per_domain_timeout,
            concurrency=concurrency,
            nameservers=nameservers,
            retries=retries,
        )
    except Exception as exc:
        return func.HttpResponse(f"Error: {exc}", status_code=500)

    return func.HttpResponse(json.dumps(result), mimetype="application/json")


# Whois: combined IP/domain lookup
@app.route(route="whois", auth_level=func.AuthLevel.FUNCTION)
def whois_lookup(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function HTTP trigger for combined whois/RDAP lookups.
    Expects `q` as a query param or JSON body.
    Optional params in JSON body: `source`, `raw`, `timeout`.
    """
    q = req.params.get("q")
    if not q:
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        q = req_body.get("q")

    if not q:
        return func.HttpResponse("Missing required parameter: q", status_code=400)

    # Build payload dict for the module
    payload = {"q": q}
    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}
    # optional fields
    for opt in ("source", "raw", "timeout"):
        if opt in req_body:
            payload[opt] = req_body[opt]

    try:
        result = whois_module.handle_request(payload)
    except ValueError as ve:
        error_obj = {"status": "error", "error": {"msg": str(ve)}}
        resp = func.HttpResponse(
            json.dumps(error_obj), status_code=400, mimetype="application/json"
        )
        return resp
    except Exception as exc:
        error_obj = {"status": "error", "error": {"msg": str(exc)}}
        resp = func.HttpResponse(
            json.dumps(error_obj), status_code=500, mimetype="application/json"
        )
        return resp

    return func.HttpResponse(json.dumps(result), mimetype="application/json")
