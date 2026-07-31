from typing import Dict, Any
import structlog

from backend.engine.sca.osv_scanner import OSVScanner

logger = structlog.get_logger("DevShield.ChainBreaker")

class ChainBreakerEngine:
    """
    Supply chain dependency vulnerability mapper using OSV database.
    """
    async def run(self, data: dict) -> Dict[str, Any]:
        target = data.get("target", "")
        manifest_name = data.get("manifest_name")
        manifest_content = data.get("manifest_content")

        scanner = OSVScanner()
        try:
            if manifest_name and manifest_content:
                return await scanner.scan_manifest(manifest_name, manifest_content)

            # Demo-compatible input: "requests==2.20.0,Django==3.1.4"
            # Optionally supports npm packages as "npm:lodash==4.17.20".
            findings = []
            package_refs = []
            analyzed = 0
            packages = [p.strip() for p in target.split(",") if p.strip()]
            for pkg in packages:
                ecosystem = "PyPI"
                if pkg.startswith("npm:"):
                    ecosystem = "npm"
                    pkg = pkg.replace("npm:", "", 1)

                if "==" in pkg:
                    name, version = pkg.split("==", 1)
                elif "@" in pkg and ecosystem == "npm":
                    name, version = pkg.rsplit("@", 1)
                else:
                    continue

                name = name.strip()
                version = version.strip()
                if name and version:
                    package_refs.append((name, version, ecosystem))

            analyzed = len(package_refs)
            for name, version, ecosystem in package_refs:
                findings.extend(await scanner.scan_package(name, version, ecosystem))

            return {
                "status": "success",
                "module": "ChainBreaker",
                "analyzed_packages": analyzed,
                "vulnerabilities_found": len(findings),
                "findings": findings
            }
        finally:
            await scanner.close()
