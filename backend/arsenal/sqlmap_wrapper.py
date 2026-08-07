import asyncio
import re
import structlog
from urllib.parse import urlparse
from typing import AsyncGenerator, Dict, Any

logger = structlog.get_logger("DevShield.Arsenal.SQLMap")


class SQLMapScanner:
    """
    DevShield Arsenal: SQLMap SQL Injection Testing Engine.
    Automated SQL injection detection and exploitation.
    """

    async def stream_test(
        self, target_url: str, level: int = 1, risk: int = 1
    ) -> AsyncGenerator[str, None]:
        """
        Stream SQLMap output. Level 1-5, Risk 1-3.
        """
        yield f"[INFO] Initializing SQLMap against: {target_url}"
        yield f"[INFO] Level: {level} | Risk: {risk} | Technique: BEUQ"

        parsed = urlparse(target_url)
        if parsed.scheme not in ('http', 'https') or not parsed.netloc:
            yield "[ERROR] Invalid URL format."
            return

        cmd = [
            "sqlmap",
            "-u", target_url,
            "--level", str(level),
            "--risk", str(risk),
            "--batch",          # Non-interactive mode
            "--output-dir", "/tmp/devshield_sqlmap",
            "--forms",
            "--crawl", "2",
            "--threads", "4",
        ]

        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
            )
            async for line in process.stdout:
                decoded = line.decode("utf-8", errors="ignore").rstrip()
                yield decoded
            await process.wait()
        except FileNotFoundError:
            yield "[ERROR] SQLMap executable not found. Please install SQLMap."
        except Exception as e:
            yield f"[ERROR] SQLMap failed: {e}"

    async def quick_test(self, target_url: str) -> Dict[str, Any]:
        """Quick injectable parameter detection."""
        results: Dict[str, Any] = {
            "target": target_url,
            "injectable": False,
            "parameters": [],
            "dbms": None,
            "severity": "LOW",
        }

        output_lines = []
        async for line in self.stream_test(target_url, level=1, risk=1):
            output_lines.append(line)
            if "is vulnerable" in line.lower() or "injection" in line.lower():
                results["injectable"] = True
                results["severity"] = "CRITICAL"
            if "back-end DBMS" in line:
                results["dbms"] = (
                    line.split(":")[-1].strip() if ":" in line else "Unknown"
                )

        # Return only the last 20 lines to keep payload lean
        results["raw_output"] = "\n".join(output_lines[-20:])
        return results


sqlmap_scanner = SQLMapScanner()
