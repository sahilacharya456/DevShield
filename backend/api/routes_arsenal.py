"""
DevShield Arsenal API Routes
============================
All REST endpoints and WebSocket streams for the Kali-tool integration hub.

Prefix  : /api/v1/arsenal   (mounted in main app)
Auth    : JWT Bearer via get_current_user (REST endpoints)
          WebSocket endpoints accept target/host in the first JSON frame.
"""

from __future__ import annotations

import asyncio
import json
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, field_validator

from backend.models.database import get_db          # noqa: F401 (available for future DB writes)
from backend.security.auth import get_current_user
from backend.models.orm import User

router = APIRouter(tags=["Arsenal"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TARGET_RE = re.compile(
    r"^(?:"
    r"(?:\d{1,3}\.){3}\d{1,3}"           # IPv4
    r"|(?:[a-fA-F0-9:]+)"                  # IPv6
    r"|(?:[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,})"  # hostname
    r")$"
)

_URL_RE = re.compile(r"^https?://", re.IGNORECASE)


def _validate_target(v: str) -> str:
    """Reject obviously invalid/dangerous target strings."""
    v = v.strip()
    if not v:
        raise ValueError("target must not be empty")
    if len(v) > 253:
        raise ValueError("target too long")
    if not _TARGET_RE.match(v):
        raise ValueError(f"'{v}' is not a valid IP address or hostname")
    return v


def _validate_url(v: str) -> str:
    v = v.strip()
    if not _URL_RE.match(v):
        raise ValueError("target_url must start with http:// or https://")
    if len(v) > 2048:
        raise ValueError("target_url too long")
    return v


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class NmapRequest(BaseModel):
    target: str
    scan_type: str = "quick"

    @field_validator("target")
    @classmethod
    def validate_target(cls, v: str) -> str:
        return _validate_target(v)

    @field_validator("scan_type")
    @classmethod
    def validate_scan_type(cls, v: str) -> str:
        allowed = {"quick", "full", "vuln", "stealth"}
        if v not in allowed:
            raise ValueError(f"scan_type must be one of {allowed}")
        return v


class SQLMapRequest(BaseModel):
    target_url: str
    level: int = 1
    risk: int = 1

    @field_validator("target_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return _validate_url(v)

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: int) -> int:
        if not (1 <= v <= 5):
            raise ValueError("level must be between 1 and 5")
        return v

    @field_validator("risk")
    @classmethod
    def validate_risk(cls, v: int) -> int:
        if not (1 <= v <= 3):
            raise ValueError("risk must be between 1 and 3")
        return v


class SSLRequest(BaseModel):
    hostname: str
    port: int = 443

    @field_validator("hostname")
    @classmethod
    def validate_hostname(cls, v: str) -> str:
        return _validate_target(v)

    @field_validator("port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError("port must be between 1 and 65535")
        return v


class WAFRequest(BaseModel):
    target_url: str

    @field_validator("target_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        return _validate_url(v)


class PortScanRequest(BaseModel):
    host: str
    ports: Optional[List[int]] = None

    @field_validator("host")
    @classmethod
    def validate_host(cls, v: str) -> str:
        return _validate_target(v)

    @field_validator("ports")
    @classmethod
    def validate_ports(cls, v: Optional[List[int]]) -> Optional[List[int]]:
        if v is not None:
            for p in v:
                if not (1 <= p <= 65535):
                    raise ValueError(f"invalid port number: {p}")
            if len(v) > 65535:
                raise ValueError("too many ports specified")
        return v


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------

@router.post("/nmap/scan", summary="Run Nmap structured scan")
async def run_nmap(
    payload: NmapRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Execute an Nmap scan against *target* and return structured port/service/
    vulnerability findings.

    Requires nmap to be installed on the host (`apt install nmap`).
    """
    from backend.arsenal.nmap_wrapper import nmap_scanner

    findings = await nmap_scanner.structured_scan(payload.target)
    return {
        "target": payload.target,
        "scan_type": payload.scan_type,
        "tool": "Nmap",
        "findings": findings,
        "finding_count": len(findings),
    }


@router.post("/ssl/audit", summary="Audit SSL/TLS configuration")
async def audit_ssl(
    payload: SSLRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Perform a comprehensive SSL/TLS audit:
    - Certificate expiry & chain
    - Protocol version (TLS 1.0/1.1 deprecated)
    - Weak cipher suites
    - Overall letter grade (A–F)
    """
    from backend.arsenal.ssl_auditor import ssl_auditor

    # ssl_auditor.audit is synchronous (uses stdlib socket); run in executor
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(
        None, ssl_auditor.audit, payload.hostname, payload.port
    )
    return results


@router.post("/waf/detect", summary="Detect WAF presence and type")
async def detect_waf(
    payload: WAFRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Probe *target_url* for a Web Application Firewall by:
    - Response header fingerprinting (Cloudflare, AWS WAF, Akamai, …)
    - Attack-payload probing (XSS, SQLi, path traversal)
    - HTTP security header audit (CSP, HSTS, X-Frame-Options, …)
    """
    from backend.arsenal.waf_detector import waf_detector

    results = await waf_detector.detect(payload.target_url)
    return results


@router.post("/ports/scan", summary="Scan open ports (Python-native)")
async def scan_ports(
    payload: PortScanRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Async TCP port scanner with banner grabbing — no nmap dependency.
    Scans up to 34 common ports by default; pass *ports* to override.
    Returns per-port risk levels and an overall risk rating.
    """
    from backend.arsenal.port_grabber import port_grabber

    results = await port_grabber.scan(payload.host, payload.ports)
    return results


@router.post("/sqlmap/test", summary="Quick SQLMap injection test")
async def test_sqli(
    payload: SQLMapRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Run sqlmap in non-interactive batch mode against *target_url*.
    Returns injectable status, detected DBMS, and a raw output tail.

    Requires sqlmap to be installed (`apt install sqlmap` or `pip install sqlmap`).
    """
    from backend.arsenal.sqlmap_wrapper import sqlmap_scanner

    result = await sqlmap_scanner.quick_test(payload.target_url)
    return result


# ---------------------------------------------------------------------------
# WebSocket endpoints
# ---------------------------------------------------------------------------

@router.websocket("/nmap/stream")
async def nmap_stream(websocket: WebSocket):
    """
    Live Nmap output streaming over WebSocket.

    Expected first frame (JSON):
        { "target": "<ip_or_host>", "scan_type": "quick|full|vuln|stealth" }

    Each server frame:
        { "line": "<output_line>", "type": "info|warning|critical|error|success|complete" }
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        scan_type = data.get("scan_type", "quick")

        if not target:
            await _ws_send(websocket, "[ERROR] No target specified.", "error")
            await websocket.close()
            return

        from backend.arsenal.nmap_wrapper import nmap_scanner

        await _ws_send(
            websocket,
            f"[INFO] Starting Nmap '{scan_type}' scan against {target}…",
            "info",
        )

        async for line in nmap_scanner.stream_scan(target, scan_type):
            await _ws_send(websocket, line, _classify_line(line))

        await _ws_send(websocket, "[COMPLETE] Nmap scan finished.", "complete")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")


@router.websocket("/ports/stream")
async def port_stream(websocket: WebSocket):
    """
    Live port-scan streaming over WebSocket.

    Expected first frame (JSON):
        { "host": "<ip_or_hostname>", "ports": [<optional list>] }

    Each server frame:
        { "line": "<output_line>", "type": "info|warning|critical|success|complete" }
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        host = (data.get("host") or "").strip()
        ports = data.get("ports")  # optional

        if not host:
            await _ws_send(websocket, "[ERROR] No host specified.", "error")
            await websocket.close()
            return

        from backend.arsenal.port_grabber import port_grabber

        await _ws_send(
            websocket,
            f"[INFO] Starting PortGrabber scan against {host}…",
            "info",
        )

        lines = await port_grabber.stream_scan(host, ports)
        for line in lines:
            await _ws_send(websocket, line, _classify_line(line))
            await asyncio.sleep(0.04)  # pacing for UI rendering

        await _ws_send(websocket, "[COMPLETE] Port scan finished.", "complete")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")


@router.websocket("/sqlmap/stream")
async def sqlmap_stream(websocket: WebSocket):
    """
    Live SQLMap output streaming over WebSocket.

    Expected first frame (JSON):
        { "target_url": "<url>", "level": 1, "risk": 1 }
    """
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target_url = (data.get("target_url") or "").strip()
        level = int(data.get("level", 1))
        risk = int(data.get("risk", 1))

        if not target_url:
            await _ws_send(websocket, "[ERROR] No target_url specified.", "error")
            await websocket.close()
            return

        from backend.arsenal.sqlmap_wrapper import sqlmap_scanner

        await _ws_send(
            websocket,
            f"[INFO] Starting SQLMap against {target_url} (level={level}, risk={risk})…",
            "info",
        )

        async for line in sqlmap_scanner.stream_test(target_url, level, risk):
            await _ws_send(websocket, line, _classify_line(line))

        await _ws_send(websocket, "[COMPLETE] SQLMap test finished.", "complete")

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")


# ---------------------------------------------------------------------------
# Private helpers

# --- Added by God Mode ---

@router.websocket("/dnsrecon/stream")
async def dnsrecon_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.dnsrecon_wrapper import dnsrecon_scanner
        async for line in dnsrecon_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] DNSRecon finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/gobuster/stream")
async def gobuster_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.gobuster_wrapper import gobuster_scanner
        async for line in gobuster_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Gobuster finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/harvester/stream")
async def harvester_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.harvester_wrapper import harvester_scanner
        async for line in harvester_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Harvester finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/hydra/stream")
async def hydra_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.hydra_wrapper import hydra_scanner
        async for line in hydra_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Hydra finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/nikto/stream")
async def nikto_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.nikto_wrapper import nikto_scanner
        async for line in nikto_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Nikto finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/shodan/stream")
async def shodan_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.shodan_wrapper import shodan_scanner
        async for line in shodan_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Shodan finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/sublister/stream")
async def sublister_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.sublister_wrapper import sublister_scanner
        async for line in sublister_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Sublister finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/whatweb/stream")
async def whatweb_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.whatweb_wrapper import whatweb_scanner
        async for line in whatweb_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] WhatWeb finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/zap/stream")
async def zap_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.zap_wrapper import zap_scanner
        async for line in zap_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] ZAP finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/hash/stream")
async def hash_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.hash_analyzer import hash_analyzer
        async for line in hash_analyzer.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Hash analysis finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")


# --- Added by God Mode ---

@router.websocket("/dnsrecon/stream")
async def dnsrecon_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.dnsrecon_wrapper import dnsrecon_scanner
        async for line in dnsrecon_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] DNSRecon finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/gobuster/stream")
async def gobuster_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.gobuster_wrapper import gobuster_scanner
        async for line in gobuster_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Gobuster finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/harvester/stream")
async def harvester_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.harvester_wrapper import harvester_scanner
        async for line in harvester_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Harvester finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/hydra/stream")
async def hydra_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.hydra_wrapper import hydra_scanner
        async for line in hydra_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Hydra finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/nikto/stream")
async def nikto_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.nikto_wrapper import nikto_scanner
        async for line in nikto_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Nikto finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/shodan/stream")
async def shodan_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.shodan_wrapper import shodan_scanner
        async for line in shodan_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Shodan finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/sublister/stream")
async def sublister_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.sublister_wrapper import sublister_scanner
        async for line in sublister_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Sublister finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/whatweb/stream")
async def whatweb_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.whatweb_wrapper import whatweb_scanner
        async for line in whatweb_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] WhatWeb finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/zap/stream")
async def zap_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.zap_wrapper import zap_scanner
        async for line in zap_scanner.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] ZAP finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

@router.websocket("/hash/stream")
async def hash_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_json()
        target = (data.get("target") or "").strip()
        from backend.arsenal.hash_analyzer import hash_analyzer
        async for line in hash_analyzer.stream_scan(target):
            await _ws_send(websocket, line, _classify_line(line))
        await _ws_send(websocket, "[COMPLETE] Hash analysis finished.", "complete")
    except Exception as e:
        await _ws_send_safe(websocket, f"[ERROR] {e}", "error")

# ---------------------------------------------------------------------------

def _classify_line(line: str) -> str:
    """Heuristically classify an output line for the frontend."""
    ll = line.lower()
    if "error" in ll:
        return "error"
    if "critical" in ll or "vulnerable" in ll or "exploit" in ll:
        return "critical"
    if "warning" in ll or "high" in ll:
        return "warning"
    if "open" in ll or "success" in ll or "found" in ll:
        return "success"
    if "complete" in ll or "summary" in ll or "finished" in ll:
        return "complete"
    return "info"


async def _ws_send(websocket: WebSocket, line: str, msg_type: str) -> None:
    """Send a typed JSON frame over *websocket*."""
    await websocket.send_text(json.dumps({"line": line, "type": msg_type}))


async def _ws_send_safe(websocket: WebSocket, line: str, msg_type: str) -> None:
    """Send a frame, ignoring errors (e.g. already-closed socket)."""
    try:
        await _ws_send(websocket, line, msg_type)
    except Exception:
        pass
