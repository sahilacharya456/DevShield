import asyncio
import structlog
from typing import List, Dict, Any, Optional

logger = structlog.get_logger("DevShield.Arsenal.PortGrabber")

# ---------------------------------------------------------------------------
# Well-known port list (scanned by default)
# ---------------------------------------------------------------------------
COMMON_PORTS: List[int] = [
    21, 22, 23, 25, 53, 80, 110, 119, 135, 139, 143, 194,
    443, 445, 465, 587, 993, 995, 1433, 1521, 1723,
    3306, 3389, 5432, 5900, 6379, 6443,
    8080, 8443, 8888, 9090, 9200, 27017,
]

# ---------------------------------------------------------------------------
# Risk metadata for well-known ports
# ---------------------------------------------------------------------------
PORT_INFO: Dict[int, Dict[str, str]] = {
    21:    {"name": "FTP",        "risk": "HIGH",     "note": "Unencrypted file transfer. Use SFTP instead."},
    22:    {"name": "SSH",        "risk": "MEDIUM",   "note": "Secure but brute-forceable. Disable root login, use key auth."},
    23:    {"name": "Telnet",     "risk": "CRITICAL", "note": "Completely unencrypted. Replace with SSH immediately."},
    25:    {"name": "SMTP",       "risk": "MEDIUM",   "note": "Mail server. Ensure SPF/DKIM/DMARC are configured."},
    53:    {"name": "DNS",        "risk": "MEDIUM",   "note": "DNS resolver. Restrict recursive queries to internal clients."},
    80:    {"name": "HTTP",       "risk": "MEDIUM",   "note": "Unencrypted web traffic. Redirect all traffic to HTTPS."},
    110:   {"name": "POP3",       "risk": "MEDIUM",   "note": "Unencrypted mail retrieval. Prefer POP3S (port 995)."},
    119:   {"name": "NNTP",       "risk": "LOW",      "note": "News protocol — rarely needed."},
    135:   {"name": "RPC",        "risk": "HIGH",     "note": "Windows RPC — exploitable (MS17-010, EternalBlue)."},
    139:   {"name": "NetBIOS",    "risk": "HIGH",     "note": "SMB over NetBIOS. Disable if not required."},
    143:   {"name": "IMAP",       "risk": "MEDIUM",   "note": "Unencrypted mail protocol. Prefer IMAPS (port 993)."},
    194:   {"name": "IRC",        "risk": "MEDIUM",   "note": "IRC — often used by malware C2."},
    443:   {"name": "HTTPS",      "risk": "LOW",      "note": "Encrypted web traffic. Verify TLS configuration."},
    445:   {"name": "SMB",        "risk": "CRITICAL", "note": "SMB — WannaCry/EternalBlue target. Block externally."},
    465:   {"name": "SMTPS",      "risk": "LOW",      "note": "Encrypted SMTP submission."},
    587:   {"name": "SMTP Sub",   "risk": "LOW",      "note": "SMTP submission (STARTTLS). Require auth."},
    993:   {"name": "IMAPS",      "risk": "LOW",      "note": "Encrypted IMAP."},
    995:   {"name": "POP3S",      "risk": "LOW",      "note": "Encrypted POP3."},
    1433:  {"name": "MSSQL",      "risk": "CRITICAL", "note": "Database exposed. Never expose to the internet."},
    1521:  {"name": "Oracle DB",  "risk": "CRITICAL", "note": "Database exposed. Restrict to internal network."},
    1723:  {"name": "PPTP",       "risk": "HIGH",     "note": "PPTP VPN — vulnerable to MS-CHAPv2 attacks. Use OpenVPN/WireGuard."},
    3306:  {"name": "MySQL",      "risk": "CRITICAL", "note": "Database exposed. Use VPN or firewall to restrict access."},
    3389:  {"name": "RDP",        "risk": "CRITICAL", "note": "Remote Desktop exposed. BlueKeep (CVE-2019-0708) exploitable."},
    5432:  {"name": "PostgreSQL", "risk": "CRITICAL", "note": "Database exposed. Use SSH tunnel or VPN."},
    5900:  {"name": "VNC",        "risk": "HIGH",     "note": "VNC exposed — often lacks encryption and is brute-forced."},
    6379:  {"name": "Redis",      "risk": "CRITICAL", "note": "Redis with no auth exposed. Full unauthenticated data access."},
    6443:  {"name": "K8s API",    "risk": "HIGH",     "note": "Kubernetes API server. Restrict access with RBAC + network policy."},
    8080:  {"name": "HTTP-Alt",   "risk": "MEDIUM",   "note": "Alternate HTTP port. Often used for dev/staging servers."},
    8443:  {"name": "HTTPS-Alt",  "risk": "LOW",      "note": "Alternate HTTPS — verify TLS config."},
    8888:  {"name": "Jupyter",    "risk": "HIGH",     "note": "Jupyter Notebook — if exposed, full code execution possible."},
    9090:  {"name": "Prometheus", "risk": "MEDIUM",   "note": "Metrics endpoint. Should not be publicly accessible."},
    9200:  {"name": "Elasticsearch", "risk": "CRITICAL", "note": "Elasticsearch exposed. Often has no auth by default."},
    27017: {"name": "MongoDB",    "risk": "CRITICAL", "note": "MongoDB exposed. Historically no auth by default."},
}

_UNKNOWN_PORT_INFO: Dict[str, str] = {
    "name": "Unknown",
    "risk": "MEDIUM",
    "note": "Unrecognised service. Investigate and close if unnecessary.",
}

# HTTP/S banner probe payloads (tried in order; first success wins)
_BANNER_PROBES: List[bytes] = [
    b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n",
    b"\r\n",   # some services respond to empty lines
]


class PortGrabber:
    """
    DevShield Arsenal: Native Python Port Scanner with Banner Grabbing.
    Fast async port discovery without an nmap dependency.
    """

    # ── Public API ─────────────────────────────────────────────────────────

    async def scan(
        self,
        host: str,
        ports: Optional[List[int]] = None,
        timeout: float = 1.5,
        concurrency: int = 100,
    ) -> Dict[str, Any]:
        """
        Scan *host* for open ports with banner grabbing.

        Args:
            host:        Target hostname or IP address.
            ports:       List of ports to scan (defaults to COMMON_PORTS).
            timeout:     TCP connection timeout in seconds.
            concurrency: Maximum simultaneous connections.

        Returns a structured dict with open_ports, counts, and overall_risk.
        """
        if ports is None:
            ports = COMMON_PORTS

        logger.info("PortGrabber scan starting", host=host, port_count=len(ports))

        sem = asyncio.Semaphore(concurrency)

        async def _limited(port: int) -> Optional[Dict[str, Any]]:
            async with sem:
                return await self._check_port(host, port, timeout)

        tasks = [_limited(port) for port in ports]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        open_ports: List[Dict[str, Any]] = [
            r
            for r in raw_results
            if r is not None and not isinstance(r, Exception)
        ]

        # Sort by port number for readability
        open_ports.sort(key=lambda p: int(p["port"]))

        # Risk aggregation
        critical_ports = [p for p in open_ports if p["risk"] == "CRITICAL"]
        high_ports     = [p for p in open_ports if p["risk"] == "HIGH"]

        if critical_ports:
            overall_risk = "CRITICAL"
        elif high_ports:
            overall_risk = "HIGH"
        elif len(open_ports) > 10:
            overall_risk = "MEDIUM"
        elif open_ports:
            overall_risk = "LOW"
        else:
            overall_risk = "NONE"

        return {
            "host": host,
            "total_scanned": len(ports),
            "open_ports": open_ports,
            "open_count": len(open_ports),
            "critical_count": len(critical_ports),
            "high_count": len(high_ports),
            "overall_risk": overall_risk,
        }

    async def stream_scan(
        self,
        host: str,
        ports: Optional[List[int]] = None,
    ) -> List[str]:
        """
        Run a port scan and return formatted log lines suitable for streaming
        over a WebSocket or SSE connection.
        """
        lines: List[str] = []
        lines.append(f"[INFO] Starting PortGrabber scan against {host}…")

        result = await self.scan(host, ports)

        lines.append(
            f"[INFO] Scanned {result['total_scanned']} ports | "
            f"{result['open_count']} open"
        )

        for p in result["open_ports"]:
            banner_snippet = (p["banner"][:60] + "…") if len(p.get("banner", "")) > 60 else (p.get("banner") or "No banner")
            lines.append(
                f"[{p['risk']}] Port {p['port']}/tcp OPEN "
                f"| {p['service']} "
                f"| {banner_snippet}"
            )
            if p.get("note"):
                lines.append(f"         ↳ {p['note']}")

        lines.append(
            f"[SUMMARY] {result['open_count']} open | "
            f"{result['critical_count']} CRITICAL | "
            f"Overall Risk: {result['overall_risk']}"
        )
        return lines

    # ── Internal helpers ────────────────────────────────────────────────────

    async def _check_port(
        self, host: str, port: int, timeout: float
    ) -> Optional[Dict[str, Any]]:
        """
        Attempt a TCP connection to *host*:*port*.
        On success, try to grab a service banner.
        Returns None if the port is closed / filtered.
        """
        try:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port),
                timeout=timeout,
            )
        except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
            return None

        banner = await self._grab_banner(reader, writer)

        try:
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

        info = PORT_INFO.get(port, _UNKNOWN_PORT_INFO)
        return {
            "port": port,
            "state": "open",
            "service": info["name"],
            "banner": banner,
            "risk": info["risk"],
            "note": info["note"],
        }

    @staticmethod
    async def _grab_banner(
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> str:
        """
        Try multiple probes to elicit a banner from the remote service.
        Returns the first non-empty response line (up to 200 chars).
        """
        # Some services send a banner immediately without a prompt
        try:
            data = await asyncio.wait_for(reader.read(512), timeout=1.0)
            if data:
                return data.decode("utf-8", errors="ignore").split("\n")[0].strip()[:200]
        except asyncio.TimeoutError:
            pass

        # Try HTTP probe
        for probe in _BANNER_PROBES:
            try:
                writer.write(probe)
                await asyncio.wait_for(writer.drain(), timeout=1.0)
                data = await asyncio.wait_for(reader.read(512), timeout=2.0)
                if data:
                    return data.decode("utf-8", errors="ignore").split("\n")[0].strip()[:200]
            except Exception:
                continue

        return ""


port_grabber = PortGrabber()
