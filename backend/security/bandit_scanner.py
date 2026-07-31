import asyncio
import os
import json
import tempfile
import structlog

logger = structlog.get_logger()

async def run_bandit(code: str) -> list:
    fd, path = tempfile.mkstemp(suffix=".py")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
        
        logger.info(f"Running bandit on {path}")
        process = await asyncio.create_subprocess_exec(
            "bandit", "-f", "json", path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        
        try:
            out_str = stdout.decode()
            if not out_str.strip():
                return []
            data = json.loads(out_str)
            results = data.get("results", [])
            vulns = []
            for r in results:
                vulns.append({
                    "id": f"bandit-{r.get('test_id')}",
                    "title": r.get('test_name'),
                    "severity": r.get('issue_severity', 'MEDIUM').upper(),
                    "description": r.get('issue_text'),
                    "line_number": r.get('line_number'),
                    "tool": "bandit"
                })
            return vulns
        except json.JSONDecodeError:
            logger.error(f"Bandit json decode error: {stdout.decode()}")
            return []
    finally:
        os.remove(path)
