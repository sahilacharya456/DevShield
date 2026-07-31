def build_codegen_prompt(task: str, language: str, security_level: str, preferences: dict) -> str:
    pref_str = "\n".join([f"- {k}: {v}" for k,v in preferences.items()])
    return f"""You are a senior secure software engineer.
Task: {task}
Language: {language}
Security Level: {security_level}

User Preferences:
{pref_str}

Please generate secure, production-ready code. Output ONLY valid {language} code inside a markdown block. No other text."""

def build_autofix_prompt(code: str, vulnerabilities: list) -> str:
    vuln_str = "\n".join([v.get("description", "") for v in vulnerabilities])
    return f"""You are an exact automated code-patching system.
The following code has these vulnerabilities:
{vuln_str}

Code:
```
{code}
```
Provide the completely fixed code inside a markdown block. Add inline comments explaining exactly what was fixed and why. Do not introduce new vulnerabilities."""

def build_security_prompt(code: str) -> str:
    return f"""Analyze the following code for vulnerabilities. Map any findings to OWASP Top 10 and CWE IDs. Provide output as a JSON array where each object has fields: title, severity (CRITICAL, HIGH, MEDIUM, LOW), description, cwe_id, owasp_top_10, line_number, remediation.
Code:
```
{code}
```
"""

def build_redteam_prompt(target: str, scan_data: str) -> str:
    return f"""You are DevShield RedAgent, an elite offensive security AI.
Your objective is to analyze the following raw reconnaissance data against the target: {target}.

Raw Scan Data:
```
{scan_data}
```

Based on this data, formulate a highly detailed Attack Path Analysis.
You MUST output your response strictly as a JSON array of vulnerability objects. Do not include any markdown formatting, backticks, or extra text. Only the raw JSON array.

Example format:
[
  {{
    "vulnerability": "Outdated OpenSSH version",
    "cve": "CVE-2023-38408",
    "epss_score": 0.85,
    "mitre_technique": "T1190: Exploit Public-Facing Application",
    "d3fend_mitigation": "D3-SP: Service Hardening",
    "exploitation_vector": "Detailed step-by-step attack path...",
    "remediation": "Update to OpenSSH 9.3p2"
  }}
]"""

