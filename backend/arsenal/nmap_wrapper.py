import asyncio
import xml.etree.ElementTree as ET
import re
import structlog
from typing import AsyncGenerator, List, Dict, Any

logger = structlog.get_logger("DevShield.Arsenal.Nmap")


class NmapScanner:
    """
    DevShield Arsenal: Nmap Network Intelligence Engine.
    Runs comprehensive port/service/vuln discovery via nmap.
    """

    async def stream_scan(
        self, target: str, scan_type: str = "full"
    ) -> AsyncGenerator[str, None]:
        """
        Stream live nmap output line by line.
        scan_type: 'quick' | 'full' | 'vuln' | 'stealth'
        """
        scan_args = {
            "quick": ["-T4", "-F", "--open"],
            "full": ["-sV", "-sC", "-T4", "-p-", "--open"],
            "vuln": ["-sV", "--script=vuln,exploit", "-T4"],
            "stealth": ["-sS", "-T2", "-f", "--data-length", "25"],
        }.get(scan_type, ["-sV", "-T4"])

        # Strict validation to prevent injection
        if not re.match(r"^[a-zA-Z0-9.-]+$", target):
            yield "[ERROR] Invalid target format."
            return

        cmd = ["nmap"] + scan_args + [target]
        logger.info("Nmap scan starting", cmd=" ".join(cmd))

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )

            async for line in process.stdout:
                yield line.decode("utf-8", errors="ignore").rstrip()

            await process.wait()
        except FileNotFoundError:
            yield "[ERROR] Nmap executable not found. Please install Nmap."
        except Exception as e:
            yield f"[ERROR] Nmap failed: {e}"

    async def structured_scan(self, target: str) -> List[Dict[str, Any]]:
        """
        Run nmap with XML output and return structured findings.
        """
        findings: List[Dict[str, Any]] = []
        if not re.match(r"^[a-zA-Z0-9.-]+$", target):
            return [{"error": "Invalid target format", "severity": "INFO"}]

        cmd = ["nmap", "-sV", "-sC", "--script=vuln", "-oX", "-", "-T4", target]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
            xml_output = stdout.decode("utf-8", errors="ignore")

            root = ET.fromstring(xml_output)
            for host in root.findall("host"):
                addr_elem = host.find("address")
                ip = (
                    addr_elem.get("addr", target)
                    if addr_elem is not None
                    else target
                )

                ports = host.find("ports")
                if ports:
                    for port_elem in ports.findall("port"):
                        portid = port_elem.get("portid", "?")
                        protocol = port_elem.get("protocol", "tcp")
                        state_elem = port_elem.find("state")
                        state = (
                            state_elem.get("state", "unknown")
                            if state_elem is not None
                            else "unknown"
                        )

                        if state != "open":
                            continue

                        service_elem = port_elem.find("service")
                        service = (
                            service_elem.get("name", "unknown")
                            if service_elem is not None
                            else "unknown"
                        )
                        version = ""
                        if service_elem is not None:
                            version = (
                                f"{service_elem.get('product', '')} "
                                f"{service_elem.get('version', '')}".strip()
                            )

                        # Collect script output (vuln results)
                        scripts: List[Dict[str, str]] = []
                        for script in port_elem.findall("script"):
                            scripts.append(
                                {
                                    "id": script.get("id", ""),
                                    "output": script.get("output", "")[:500],
                                }
                            )

                        severity = "LOW"
                        if any(
                            s["id"]
                            in [
                                "vuln",
                                "exploit",
                                "http-shellshock",
                                "ms17-010",
                            ]
                            for s in scripts
                        ):
                            severity = "CRITICAL"
                        elif portid in ["21", "23", "3389", "4444"]:
                            severity = "HIGH"
                        elif service in ["http", "https", "ftp", "ssh"]:
                            severity = "MEDIUM"

                        findings.append(
                            {
                                "ip": ip,
                                "port": portid,
                                "protocol": protocol,
                                "state": state,
                                "service": service,
                                "version": version,
                                "severity": severity,
                                "scripts": scripts,
                            }
                        )
        except asyncio.TimeoutError:
            findings.append(
                {
                    "error": "Scan timed out after 120 seconds",
                    "severity": "INFO",
                }
            )
        except ET.ParseError:
            findings.append(
                {
                    "error": "Could not parse nmap XML output",
                    "severity": "INFO",
                }
            )
        except Exception as e:
            findings.append({"error": str(e), "severity": "INFO"})

        return findings


nmap_scanner = NmapScanner()
