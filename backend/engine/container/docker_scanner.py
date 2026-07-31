import structlog
from typing import List, Dict, Any
from dockerfile_parse import DockerfileParser

logger = structlog.get_logger("DevShield.Container")

class DockerScanner:
    """
    True Container scanning engine using Dockerfile AST parsing.
    Replaces naive regex line matching.
    """
    
    def scan_dockerfile(self, content: str) -> List[Dict[str, Any]]:
        findings = []
        dfp = DockerfileParser()
        dfp.content = content
        
        # 1. Check for USER directive (Run as non-root)
        has_user = False
        
        # 2. Check for unsafe ADD (vs COPY)
        
        for instruction in dfp.structure:
            directive = instruction.get('instruction', '').upper()
            value = instruction.get('value', '')
            line_no = instruction.get('startline', 0) + 1
            
            if directive == 'USER':
                if value.strip() != 'root':
                    has_user = True
                    
            if directive == 'ADD':
                if not value.startswith('http'): # Remote URLs are okayish, but local ADD can extract archives unexpectedly
                    findings.append({
                        "title": "Unsafe ADD directive",
                        "severity": "LOW",
                        "confidence": 100,
                        "line": line_no,
                        "description": "Use COPY instead of ADD for local files to prevent unintended archive extraction.",
                        "cwe": "CWE-73",
                        "owasp": "A05:2021-Security Misconfiguration"
                    })
                    
            if directive == 'RUN':
                if 'curl' in value and '|' in value and ('sh' in value or 'bash' in value):
                    findings.append({
                        "title": "Unsafe Pipe to Shell",
                        "severity": "CRITICAL",
                        "confidence": 100,
                        "line": line_no,
                        "description": "Fetching a script from the internet and piping it directly to shell is dangerous.",
                        "cwe": "CWE-78",
                        "owasp": "A03:2021-Injection"
                    })
                    
            if directive == 'COPY':
                if value.strip().startswith('. .'):
                    findings.append({
                        "title": "Blind COPY directive",
                        "severity": "MEDIUM",
                        "confidence": 100,
                        "line": line_no,
                        "description": "COPY . . pulls in entire directories including secrets (.git, .env). Use specific paths.",
                        "cwe": "CWE-200",
                        "owasp": "A05:2021-Security Misconfiguration"
                    })

        if not has_user:
            findings.append({
                "title": "Running as Root Container",
                "severity": "HIGH",
                "confidence": 100,
                "line": 1,
                "description": "No USER directive found. Container processes will run as root. Specify a non-root USER.",
                "cwe": "CWE-250",
                "owasp": "A01:2021-Broken Access Control"
            })
            
        # Check base image
        if dfp.baseimage and dfp.baseimage.endswith(":latest"):
            findings.append({
                "title": "Unpinned Base Image",
                "severity": "MEDIUM",
                "confidence": 100,
                "line": 1,
                "description": f"Base image '{dfp.baseimage}' uses 'latest' tag. Pin to a specific hash or version.",
                "cwe": "CWE-668",
                "owasp": "A06:2021-Vulnerable and Outdated Components"
            })

        return findings

def run_container_scan(dockerfile_content: str) -> List[Dict[str, Any]]:
    scanner = DockerScanner()
    return scanner.scan_dockerfile(dockerfile_content)
