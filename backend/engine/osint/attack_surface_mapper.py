import asyncio
import ipaddress
import socket
from typing import Any, Dict, List
from urllib.parse import urlparse

import httpx
import structlog

from backend.config import settings

logger = structlog.get_logger("DevShield.OsintRadar")

COMMON_PORTS = [21, 22, 25, 53, 80, 110, 143, 443, 445, 993, 995, 3306, 3389, 5900, 8080, 8443]


class OsintRadarEngine:
    """
    Passive-first attack surface and exploit intelligence mapper.

    Uses public NVD CVE search without a key and enriches with Shodan/VirusTotal
    when API keys are configured. Active probing is opt-in through options.
    """

    def _normalize_target(self, target: str) -> str:
        raw = (target or "127.0.0.1").strip()
        parsed = urlparse(raw if "://" in raw else f"//{raw}")
        return parsed.hostname or raw.split("/")[0]

    def _resolve(self, host: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {"host": host, "addresses": []}
        try:
            infos = socket.getaddrinfo(host, None)
            addresses = sorted({info[4][0] for info in infos})
            result["addresses"] = [
                {
                    "ip": ip,
                    "is_private": ipaddress.ip_address(ip).is_private,
                    "is_loopback": ipaddress.ip_address(ip).is_loopback,
                }
                for ip in addresses
            ]
        except Exception as exc:
            result["error"] = str(exc)
        return result

    def _is_allowed_active_target(self, host: str, dns: Dict[str, Any]) -> bool:
        allowed = [item.strip().lower() for item in settings.allowed_scan_targets.split(",") if item.strip()]
        if allowed and not any(host.lower() == item or host.lower().endswith(f".{item}") for item in allowed):
            return False
        if not settings.allow_private_scan_targets:
            for address in dns.get("addresses", []):
                if address.get("is_private") or address.get("is_loopback"):
                    return False
        return True

    async def _fetch_http_headers(self, host: str) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True) as client:
            for scheme in ("https", "http"):
                try:
                    response = await client.head(f"{scheme}://{host}")
                    headers = {key: value for key, value in response.headers.items()}
                    headers["_url"] = str(response.url)
                    headers["_status_code"] = str(response.status_code)
                    break
                except Exception:
                    continue
        return headers

    async def _active_port_probe(self, host: str) -> List[int]:
        async def check(port: int) -> int | None:
            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1.0)
                writer.close()
                await writer.wait_closed()
                return port
            except Exception:
                return None

        results = await asyncio.gather(*(check(port) for port in COMMON_PORTS))
        return [port for port in results if port is not None]

    async def _nvd_search(self, keyword: str) -> List[Dict[str, Any]]:
        headers = {"apiKey": settings.nvd_api_key} if settings.nvd_api_key else {}
        params = {"keywordSearch": keyword, "resultsPerPage": 10}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get("https://services.nvd.nist.gov/rest/json/cves/2.0", params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            logger.warning(f"NVD search failed for {keyword}: {exc}")
            return []

        findings: List[Dict[str, Any]] = []
        for item in data.get("vulnerabilities", []):
            cve = item.get("cve", {})
            metrics = cve.get("metrics", {})
            cvss = (
                metrics.get("cvssMetricV31")
                or metrics.get("cvssMetricV30")
                or metrics.get("cvssMetricV2")
                or []
            )
            severity = cvss[0].get("cvssData", {}).get("baseSeverity", "UNKNOWN") if cvss else "UNKNOWN"
            descriptions = cve.get("descriptions", [])
            summary = next((d.get("value") for d in descriptions if d.get("lang") == "en"), "")
            findings.append({
                "id": cve.get("id"),
                "severity": severity,
                "published": cve.get("published"),
                "last_modified": cve.get("lastModified"),
                "summary": summary,
                "source_url": f"https://nvd.nist.gov/vuln/detail/{cve.get('id')}",
            })
        return findings

    async def _shodan_host(self, ip: str) -> Dict[str, Any] | None:
        if not settings.shodan_api_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"https://api.shodan.io/shodan/host/{ip}", params={"key": settings.shodan_api_key})
                response.raise_for_status()
                data = response.json()
                return {
                    "ip": ip,
                    "ports": data.get("ports", []),
                    "hostnames": data.get("hostnames", []),
                    "org": data.get("org"),
                    "vulns": sorted((data.get("vulns") or {}).keys()),
                }
        except Exception as exc:
            logger.warning(f"Shodan lookup failed for {ip}: {exc}")
            return {"ip": ip, "error": str(exc)}

    async def _virustotal_domain(self, host: str) -> Dict[str, Any] | None:
        if not settings.virustotal_api_key:
            return None
        try:
            async with httpx.AsyncClient(timeout=10.0, headers={"x-apikey": settings.virustotal_api_key}) as client:
                response = await client.get(f"https://www.virustotal.com/api/v3/domains/{host}")
                response.raise_for_status()
                data = response.json().get("data", {}).get("attributes", {})
                return {
                    "last_analysis_stats": data.get("last_analysis_stats", {}),
                    "reputation": data.get("reputation"),
                    "categories": data.get("categories", {}),
                }
        except Exception as exc:
            logger.warning(f"VirusTotal lookup failed for {host}: {exc}")
            return {"error": str(exc)}

    def _risk_score(self, cves: List[Dict[str, Any]], ports: List[int], shodan: List[Dict[str, Any]]) -> int:
        score = min(40, len(ports) * 5)
        score += min(40, sum(10 for cve in cves if cve.get("severity") in {"HIGH", "CRITICAL"}))
        score += min(20, sum(len(item.get("vulns", [])) for item in shodan if item))
        return min(score, 100)

    async def run(self, data: dict) -> Dict[str, Any]:
        target = self._normalize_target(data.get("target", "127.0.0.1"))
        options = data.get("options") or {}
        active_probe = bool(options.get("active_probe"))
        cve_keyword = str(options.get("cve_keyword") or target)

        dns = self._resolve(target)
        if active_probe and not self._is_allowed_active_target(target, dns):
            return {
                "status": "error",
                "module": "OsintRadar",
                "target": target,
                "message": "Target is not allowed by active scan policy",
            }
        headers_task = self._fetch_http_headers(target)
        nvd_task = self._nvd_search(cve_keyword)
        vt_task = self._virustotal_domain(target)
        ports_task = self._active_port_probe(target) if active_probe else asyncio.sleep(0, result=[])

        shodan_tasks = [
            self._shodan_host(addr["ip"])
            for addr in dns.get("addresses", [])
            if not addr.get("is_private") and not addr.get("is_loopback")
        ]

        headers, cves, vt, open_ports = await asyncio.gather(headers_task, nvd_task, vt_task, ports_task)
        shodan_results = [item for item in await asyncio.gather(*shodan_tasks)] if shodan_tasks else []

        return {
            "status": "success",
            "module": "OsintRadar",
            "target": target,
            "mode": "active_probe" if active_probe else "passive",
            "dns": dns,
            "http_headers": headers,
            "open_ports": open_ports,
            "nvd_cves": cves,
            "shodan": shodan_results,
            "virustotal": vt,
            "api_keys": {
                "shodan_configured": bool(settings.shodan_api_key),
                "virustotal_configured": bool(settings.virustotal_api_key),
                "nvd_configured": bool(settings.nvd_api_key),
            },
            "surface_risk_score": self._risk_score(cves, open_ports, shodan_results),
        }
