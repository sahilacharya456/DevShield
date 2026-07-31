import subprocess
import tempfile
import json
import logging
from typing import List, Dict

from engine.ai.router import AIRouter

logger = logging.getLogger("DevShield.SecurityPipeline")

class SecurityPipeline:
    @staticmethod
    async def run_semgrep(code: str, language: str) -> List[Dict]:
        """Runs Semgrep static analysis locally inside a temp directory."""
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
            f.write(code)
            temp_path = f.name
            
        try:
            # Note: For production, path to rules needs to be injected from settings
            # We use basic auto ruleset for MVP
            cmd = ["semgrep", "--json", "--auto", temp_path]
            # [FIXED] Security Audit Patch: Enforced 30s timeout and strictly disabled shell execution to prevent injection.
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=False)
            
            if not result.stdout:
                return []
                
            report = json.loads(result.stdout)
            findings = []
            for item in report.get("results", []):
                findings.append({
                    "name": item.get("check_id"),
                    "severity": item.get("extra", {}).get("severity", "WARNING").upper(),
                    "line": item.get("start", {}).get("line"),
                    "description": item.get("extra", {}).get("message"),
                    "source": "Semgrep",
                })
            return findings
        except Exception as e:
            logger.error(f"Semgrep execution failed: {e}")
            return []
        finally:
            import os
            os.remove(temp_path)

    @staticmethod
    async def run_ai_analysis(code: str) -> List[Dict]:
        """Use the AIRouter to identify logic flaws Semgrep missed."""
        prompt = f"""Analyze this code for high-risk, complex logic vulnerabilities that static analysis might miss.
Output valid JSON:
{{
  "vulnerabilities": [
    {{"name": "vuln_name", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "line": 10, "description": "detail"}}
  ]
}}

Code:
{code}
"""
        response_text = await AIRouter.generate(prompt=prompt, json_mode=True)
        try:
            data = json.loads(response_text)
            vulns = data.get("vulnerabilities", [])
            for v in vulns:
                v["source"] = "AI_Analyzer"
            return vulns
        except Exception as e:
            logger.error(f"AI Analysis parsing failed: {e}")
            return []

    @classmethod
    async def analyze(cls, code: str, language: str) -> Dict:
        """Orchestrate multi-engine scan."""
        static_findings = await cls.run_semgrep(code, language)
        ai_findings = await cls.run_ai_analysis(code)
        
        all_vulns = static_findings + ai_findings
        
        return {
            "total_issues": len(all_vulns),
            "vulnerabilities": all_vulns,
        }
