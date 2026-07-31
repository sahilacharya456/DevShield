import pytest

from backend.engine.osint.attack_surface_mapper import OsintRadarEngine
from backend.engine.quantum.pqc_auditor import pqc_auditor
from backend.engine.redteam.red_agent import RedAgentEngine


@pytest.mark.asyncio
async def test_redagent_defaults_to_planning_only():
    result = await RedAgentEngine().run({"target": "127.0.0.1"})

    assert result["status"] == "success"
    assert result["authorization_confirmed"] is False
    assert result["executed_steps"] == []
    assert result["attack_plan"]


@pytest.mark.asyncio
async def test_redagent_authorized_uses_builtin_probe(monkeypatch):
    engine = RedAgentEngine()

    async def fake_scan(host, ports=None):
        assert host == "127.0.0.1"
        return [80, 443]

    monkeypatch.setattr(engine, "_socket_port_scan", fake_scan)

    result = await engine.run({
        "target": "127.0.0.1",
        "options": {"authorization_confirmed": True, "execute_tools": False},
    })

    assert result["authorization_confirmed"] is True
    assert result["open_ports"] == [80, 443]
    assert result["executed_steps"] == []


@pytest.mark.asyncio
async def test_redagent_blocks_disallowed_target(monkeypatch):
    from backend.engine.redteam import red_agent

    monkeypatch.setattr(red_agent.settings, "allowed_scan_targets", "allowed.example")
    monkeypatch.setattr(
        RedAgentEngine,
        "_resolve_target",
        lambda self, host: {"host": host, "ip": "93.184.216.34", "is_private": False, "is_loopback": False},
    )

    result = await RedAgentEngine().run({"target": "blocked.example"})

    assert result["status"] == "error"
    assert "not allowed" in result["message"]


@pytest.mark.asyncio
async def test_osint_passive_aggregation(monkeypatch):
    engine = OsintRadarEngine()

    monkeypatch.setattr(engine, "_resolve", lambda host: {"host": host, "addresses": [{"ip": "93.184.216.34", "is_private": False, "is_loopback": False}]})

    async def fake_headers(host):
        return {"server": "example"}

    async def fake_nvd(keyword):
        return [{"id": "CVE-2099-0001", "severity": "HIGH"}]

    async def fake_vt(host):
        return {"reputation": 0}

    async def fake_shodan(ip):
        return {"ip": ip, "ports": [443], "vulns": ["CVE-2099-0001"]}

    monkeypatch.setattr(engine, "_fetch_http_headers", fake_headers)
    monkeypatch.setattr(engine, "_nvd_search", fake_nvd)
    monkeypatch.setattr(engine, "_virustotal_domain", fake_vt)
    monkeypatch.setattr(engine, "_shodan_host", fake_shodan)

    result = await engine.run({"target": "example.com", "options": {"cve_keyword": "nginx"}})

    assert result["mode"] == "passive"
    assert result["http_headers"]["server"] == "example"
    assert result["nvd_cves"][0]["id"] == "CVE-2099-0001"
    assert result["surface_risk_score"] > 0


@pytest.mark.asyncio
async def test_osint_active_probe_blocks_disallowed_target(monkeypatch):
    from backend.engine.osint import attack_surface_mapper

    engine = OsintRadarEngine()
    monkeypatch.setattr(attack_surface_mapper.settings, "allowed_scan_targets", "allowed.example")
    monkeypatch.setattr(engine, "_resolve", lambda host: {"host": host, "addresses": []})

    result = await engine.run({"target": "blocked.example", "options": {"active_probe": True}})

    assert result["status"] == "error"
    assert "not allowed" in result["message"]


def test_quantum_ast_detects_imports_and_calls():
    code = """
import hashlib
from Crypto.PublicKey import RSA
from Crypto.Cipher import DES
from cryptography.hazmat.primitives.asymmetric import ec

digest = hashlib.md5(data).hexdigest()
key = RSA.generate(2048)
private_key = ec.generate_private_key(ec.SECP256R1())
"""

    result = pqc_auditor.audit_ast(code)
    titles = [finding["title"] for finding in result["findings"]]

    assert any("MD5" in title for title in titles)
    assert any("RSA" in title for title in titles)
    assert any("ECC" in title or "Elliptic" in title for title in titles)
    assert any("DES" in title for title in titles)
