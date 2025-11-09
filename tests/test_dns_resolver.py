import asyncio
from types import SimpleNamespace

import dns.exception
import dns.resolver

from functions.dns_resolver import resolve_domains_async


class FakeRR:
    def __init__(self, text, ttl=60, target=False):
        self._text = text
        self.rrset = SimpleNamespace(ttl=ttl)
        if target:
            self.target = SimpleNamespace(to_text=lambda: text)

    def to_text(self):
        return self._text


class FakeAnswer(list):
    def __init__(self, items, ttl=60):
        super().__init__(items)
        self.rrset = SimpleNamespace(ttl=ttl)


class FakeResolver:
    def __init__(self, behavior):
        # behavior: dict of (name, rtype) -> either FakeAnswer or Exception to raise
        self.behavior = behavior
        self.nameservers = None
        self.lifetime = None
        self.timeout = None

    async def resolve(self, name, rtype):
        key = (name, rtype)
        val = self.behavior.get(key)
        if isinstance(val, Exception):
            raise val
        return val


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_resolve_success(monkeypatch):
    behavior = {
        ("example.com", "A"): FakeAnswer([FakeRR("1.2.3.4")]),
        ("example.com", "AAAA"): FakeAnswer([]),
        ("example.com", "NS"): FakeAnswer([FakeRR("ns1.example.com.")]),
        ("example.com", "RRSIG"): dns.resolver.NoAnswer(),
        ("example.com", "DNSKEY"): dns.resolver.NoAnswer(),
    }

    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: FakeResolver(behavior))

    results = run(resolve_domains_async(["example.com"], retries=0, concurrency=1))
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is True
    assert "1.2.3.4" in r["ip_addresses"]
    assert r["name_servers"] == ["ns1.example.com."]
    assert r["dnssec"] == "unsigned"
    assert r["error"] is None


def test_resolve_nxdomain(monkeypatch):
    behavior = {
        ("nope.invalid", "A"): dns.resolver.NXDOMAIN(),
    }
    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: FakeResolver(behavior))

    results = run(resolve_domains_async(["nope.invalid"], retries=0, concurrency=1))
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is False
    assert r["error"] is not None
    assert r["error"]["type"] == "NXDOMAIN"


def test_resolve_rrsig_present(monkeypatch):
    behavior = {
        ("signed.example", "A"): FakeAnswer([FakeRR("2.2.2.2")]),
        ("signed.example", "AAAA"): FakeAnswer([]),
        ("signed.example", "NS"): FakeAnswer([FakeRR("ns.signed.")]),
        ("signed.example", "RRSIG"): FakeAnswer([FakeRR("sigdata")]),
        ("signed.example", "DNSKEY"): dns.resolver.NoAnswer(),
    }
    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: FakeResolver(behavior))

    results = run(resolve_domains_async(["signed.example"], retries=0, concurrency=1))
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is True
    assert r["dnssec"] == "signed-present"


def test_cname_loop(monkeypatch):
    # CNAME points to itself -> should detect loop and return error
    behavior = {
        ("loop.example", "CNAME"): FakeAnswer([FakeRR("loop.example", target=True)]),
        ("loop.example", "A"): dns.resolver.NoAnswer(),
    }
    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: FakeResolver(behavior))

    results = run(resolve_domains_async(["loop.example"], retries=0, concurrency=1))
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is False
    assert r["error"] is not None
    assert r["error"]["type"] == "RuntimeError"


def test_timeout_retries(monkeypatch):
    # Simulate timeout on A query to trigger retry logic
    behavior = {
        ("slow.example", "A"): dns.exception.Timeout(),
        ("slow.example", "AAAA"): dns.resolver.NoAnswer(),
    }
    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: FakeResolver(behavior))

    results = run(resolve_domains_async(["slow.example"], retries=2, concurrency=1))
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is False
    assert r["error"] is not None
    # Timeout class name is 'Timeout'
    assert r["error"]["type"] == "Timeout"
    # metrics.retries should equal the configured retries
    assert r["metrics"]["retries"] == 2


def test_noanswer_no_ips_but_ns(monkeypatch):
    # Domain with NS present but no A/AAAA - NoAnswer should be reported
    behavior = {
        ("noips.example", "A"): dns.resolver.NoAnswer(),
        ("noips.example", "AAAA"): dns.resolver.NoAnswer(),
        ("noips.example", "NS"): FakeAnswer([FakeRR("ns.noips.example.")]),
    }
    monkeypatch.setattr("dns.asyncresolver.Resolver", lambda: FakeResolver(behavior))

    results = run(resolve_domains_async(["noips.example"], retries=0, concurrency=1))
    assert len(results) == 1
    r = results[0]
    assert r["resolvable"] is False
    # Because A/AAAA NoAnswer causes the domain worker to raise before NS is fetched,
    # the resolver may not populate name_servers in this error path.
    assert r["name_servers"] == []
    assert r["error"] is not None
    assert r["error"]["type"] == "NoAnswer"
