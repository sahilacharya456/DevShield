import asyncio
import json
import re
from typing import List, Dict, Any, Iterable, Tuple

import httpx
import structlog

logger = structlog.get_logger("DevShield.SCA")

OSV_API_URL = "https://api.osv.dev/v1/query"
PackageRef = Tuple[str, str, str]


def _clean_version_spec(spec: str) -> str:
    """
    Convert common package.json version specs to an exact-ish version when possible.
    OSV package queries need a concrete version, so unsupported ranges are skipped.
    """
    spec = (spec or "").strip()
    if not spec:
        return ""
    spec = re.sub(r"^(npm:)?", "", spec)
    spec = re.sub(r"^[~^<>=\s]+", "", spec)
    match = re.match(r"(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)", spec)
    return match.group(1) if match else ""


def parse_requirements(requirements_text: str) -> List[PackageRef]:
    packages: List[PackageRef] = []
    for raw_line in requirements_text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        line = line.split("#", 1)[0].split(";", 1)[0].strip()
        if "==" not in line:
            continue
        name, version = line.split("==", 1)
        name = name.strip()
        version = version.strip()
        if name and version:
            packages.append((name, version, "PyPI"))
    return packages


def parse_package_json(package_json_text: str) -> List[PackageRef]:
    try:
        data = json.loads(package_json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid package.json: {exc}") from exc

    packages: List[PackageRef] = []
    for section in ("dependencies", "devDependencies", "optionalDependencies"):
        deps = data.get(section, {})
        if not isinstance(deps, dict):
            continue
        for name, spec in deps.items():
            version = _clean_version_spec(str(spec))
            if name and version:
                packages.append((name, version, "npm"))
    return packages


def _walk_lock_dependencies(dependencies: Dict[str, Any]) -> Iterable[PackageRef]:
    for name, meta in dependencies.items():
        if not isinstance(meta, dict):
            continue
        version = str(meta.get("version") or "").strip()
        if name and version:
            yield (name, version, "npm")
        nested = meta.get("dependencies")
        if isinstance(nested, dict):
            yield from _walk_lock_dependencies(nested)


def parse_package_lock(package_lock_text: str) -> List[PackageRef]:
    try:
        data = json.loads(package_lock_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid package-lock.json: {exc}") from exc

    packages: List[PackageRef] = []
    lock_packages = data.get("packages")
    if isinstance(lock_packages, dict):
        for path, meta in lock_packages.items():
            if not path.startswith("node_modules/") or not isinstance(meta, dict):
                continue
            name = path.replace("node_modules/", "", 1)
            version = str(meta.get("version") or "").strip()
            if name and version:
                packages.append((name, version, "npm"))

    dependencies = data.get("dependencies")
    if isinstance(dependencies, dict):
        packages.extend(_walk_lock_dependencies(dependencies))

    return list(dict.fromkeys(packages))


def parse_manifest(manifest_name: str, manifest_content: str) -> List[PackageRef]:
    normalized_name = manifest_name.lower().split("/")[-1].split("\\")[-1]
    if normalized_name in {"requirements.txt", "requirements-dev.txt"} or normalized_name.endswith(".requirements.txt"):
        return parse_requirements(manifest_content)
    if normalized_name == "package.json":
        return parse_package_json(manifest_content)
    if normalized_name == "package-lock.json":
        return parse_package_lock(manifest_content)
    raise ValueError(f"Unsupported manifest type: {manifest_name}")


def _fixed_versions(vuln: Dict[str, Any]) -> List[str]:
    fixed: List[str] = []
    for affected in vuln.get("affected", []) or []:
        for item in affected.get("ranges", []) or []:
            for event in item.get("events", []) or []:
                if "fixed" in event:
                    fixed.append(event["fixed"])
    return sorted(set(fixed))


def _severity(vuln: Dict[str, Any]) -> str:
    for severity in vuln.get("severity", []) or []:
        score = severity.get("score", "")
        if "CVSS:" in score:
            if "/C:H" in score and "/I:H" in score and "/A:H" in score:
                return "CRITICAL"
            if any(flag in score for flag in ("/C:H", "/I:H", "/A:H")):
                return "HIGH"
    return "HIGH"

class OSVScanner:
    """
    True SCA engine using the live OSV API.
    Replaces the hardcoded 5-package string matching.
    """
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def scan_package(self, name: str, version: str, ecosystem: str = "PyPI") -> List[Dict[str, Any]]:
        payload = {
            "version": version,
            "package": {
                "name": name,
                "ecosystem": ecosystem
            }
        }
        
        try:
            response = await self.client.post(OSV_API_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            
            if "vulns" not in data:
                return []
                
            findings = []
            for vuln in data["vulns"]:
                vuln_id = vuln.get("id", "Unknown")
                summary = vuln.get("summary", "No summary provided")
                details = vuln.get("details", "")
                aliases = vuln.get("aliases", [])
                cve_id = next((a for a in aliases if a.startswith("CVE-")), vuln_id)
                severity_str = _severity(vuln)
                source_url = f"https://osv.dev/vulnerability/{vuln_id}"

                findings.append({
                    "title": f"Vulnerable Dependency: {name}@{version}",
                    "package": name,
                    "version": version,
                    "ecosystem": ecosystem,
                    "vulnerability_id": vuln_id,
                    "aliases": aliases,
                    "cve": cve_id,
                    "severity": severity_str,
                    "confidence": 100,
                    "line": 1,
                    "summary": summary,
                    "description": f"{summary}\n{details[:200]}...",
                    "fixed_versions": _fixed_versions(vuln),
                    "source_url": source_url,
                    "osv_url": source_url,
                })
                
            return findings
            
        except httpx.HTTPError as e:
            logger.error(f"OSV API Error for {name}@{version}: {e}")
            return []
            
    async def scan_requirements(self, requirements_text: str) -> List[Dict[str, Any]]:
        """
        Parses requirements.txt format and queries OSV concurrently.
        """
        findings = []
        tasks = [
            self.scan_package(name, version, ecosystem)
            for name, version, ecosystem in parse_requirements(requirements_text)
        ]
        if not tasks:
            return []
            
        results = await asyncio.gather(*tasks)
        for r in results:
            findings.extend(r)
            
        return findings

    async def scan_manifest(self, manifest_name: str, manifest_content: str) -> Dict[str, Any]:
        packages = parse_manifest(manifest_name, manifest_content)
        tasks = [
            self.scan_package(name, version, ecosystem)
            for name, version, ecosystem in packages
        ]

        findings: List[Dict[str, Any]] = []
        if tasks:
            results = await asyncio.gather(*tasks)
            for result in results:
                findings.extend(result)

        return {
            "status": "success",
            "module": "ChainBreaker",
            "manifest_name": manifest_name,
            "analyzed_packages": len(packages),
            "vulnerabilities_found": len(findings),
            "findings": findings,
        }

    async def close(self):
        await self.client.aclose()

async def run_sca(requirements_text: str) -> List[Dict[str, Any]]:
    scanner = OSVScanner()
    try:
        return await scanner.scan_requirements(requirements_text)
    finally:
        await scanner.close()


async def run_sca_manifest(manifest_name: str, manifest_content: str) -> Dict[str, Any]:
    scanner = OSVScanner()
    try:
        return await scanner.scan_manifest(manifest_name, manifest_content)
    finally:
        await scanner.close()
