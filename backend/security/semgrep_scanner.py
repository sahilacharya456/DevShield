import asyncio
import os
import json
import tempfile
import structlog

logger = structlog.get_logger()

async def run_semgrep(code: str, ext: str = ".py") -> list:
    fd, path = tempfile.mkstemp(suffix=ext)
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(code)
            
        logger.info(f"Running semgrep on {path}")
        process = await asyncio.create_subprocess_exec(
            "semgrep", "scan", "--json", "--config=auto", path,
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
                extra = r.get("extra", {})
                vulns.append({
                    "id": f"semgrep-{r.get('check_id')}",
                    "title": r.get('check_id'),
                    "severity": extra.get('severity', 'WARNING').upper(),
                    "description": extra.get('message'),
                    "line_number": r.get('start', {}).get('line'),
                    "tool": "semgrep"
                })
            return vulns
        except json.JSONDecodeError:
            logger.error(f"Semgrep json decode error: {stdout.decode()}")
            return []
    finally:
        os.remove(path)
