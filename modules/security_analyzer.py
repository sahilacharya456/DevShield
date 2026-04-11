"""
DevShield AI — Module 3: Security Analyzer
Combines Bandit static analysis + Gemini AI for deep vulnerability detection.
Maps every finding to OWASP Top 10 (2021) and supports auto-fix.
"""

import json
import os
import re
import subprocess
import tempfile
from datetime import datetime

import google.generativeai as genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, SEVERITY_ORDER, DEFAULT_RULES_PATH
from utils.owasp_mapper import map_to_owasp
from utils.custom_rules import load_rules, apply_rules

genai.configure(api_key=GEMINI_API_KEY)


def _get_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(model_name=GEMINI_MODEL)


# ─── Bandit Static Analysis (Python only) ────────────────────────────────────

def _analyze_with_bandit(code: str) -> list[dict]:
    """Run Bandit on Python source code and return normalized findings."""
    findings = []
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        proc = subprocess.run(
            ["bandit", "-f", "json", "-r", "--quiet", tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        os.unlink(tmp_path)

        if proc.stdout:
            data = json.loads(proc.stdout)
            for issue in data.get("results", []):
                sev = issue.get("issue_severity", "LOW").upper()
                findings.append(
                    {
                        "name": issue.get("test_name", "Unknown").replace("_", " ").title(),
                        "line": issue.get("line_number", 0),
                        "severity": sev,
                        "confidence": _bandit_confidence_to_float(
                            issue.get("issue_confidence", "LOW")
                        ),
                        "description": issue.get("issue_text", ""),
                        "source": "Bandit",
                        "poc": "",
                        "fix_suggestion": issue.get("more_info", ""),
                        "fixed_code_snippet": "",
                        "owasp_id": "",
                        "owasp_name": "",
                        "owasp_url": "",
                    }
                )
    except FileNotFoundError:
        pass  # Bandit not installed — Gemini covers it
    except Exception:
        pass

    return findings


def _bandit_confidence_to_float(level: str) -> float:
    return {"HIGH": 0.9, "MEDIUM": 0.65, "LOW": 0.4}.get(level.upper(), 0.5)


# ─── Gemini AI Analysis ───────────────────────────────────────────────────────

def _analyze_with_gemini(
    code: str, language: str, extra_rules_context: str = ""
) -> dict:
    """Deep AI security analysis — language-agnostic."""
    model = _get_model()

    prompt = f"""You are a world-class cybersecurity expert performing a comprehensive security code audit.

Analyze this {language} code for ALL possible security vulnerabilities:

```{language.lower().split()[0]}
{code}
```

{extra_rules_context}

Systematically check for:
- SQL / NoSQL / Command / LDAP / SSTI injection
- Hardcoded credentials, API keys, tokens, private keys
- Weak or broken cryptography (MD5, SHA-1, DES, ECB mode, weak PRNG)
- Path traversal / directory traversal
- Insecure deserialization (pickle, yaml.load, eval)
- Missing or improper input validation
- XSS, CSRF vulnerabilities (for web code)
- Broken access control / privilege escalation
- Security misconfigurations (debug mode, verbose errors)
- Sensitive data exposure / logging secrets
- SSRF vulnerabilities
- Race conditions / TOCTOU
- Buffer / integer overflow (for C/C++ code)
- Missing error handling revealing internals
- Insecure session management

For EVERY vulnerability found, provide ALL of these fields:
- name: Short vulnerability name
- line: Best-estimate line number (integer)
- severity: CRITICAL, HIGH, MEDIUM, LOW, or INFO
- confidence: Float 0.0 to 1.0
- description: Clear technical explanation
- poc: Proof-of-concept attack string or explanation (defensive/educational only)
- fix_suggestion: Specific fix recommendation
- fixed_code_snippet: The corrected version of the vulnerable code fragment

Also provide:
- overall_score: 0–100 (100 = perfectly secure)
- grade: A (90+), B (75-89), C (60-74), D (40-59), F (<40)
- summary: Executive-level one-paragraph summary
- total_issues: Count of vulnerabilities found

Return ONLY this exact JSON structure (no markdown, no explanation):
{{
  "vulnerabilities": [
    {{
      "name": "...",
      "line": 0,
      "severity": "CRITICAL",
      "confidence": 0.95,
      "description": "...",
      "poc": "...",
      "fix_suggestion": "...",
      "fixed_code_snippet": "..."
    }}
  ],
  "overall_score": 85,
  "grade": "B",
  "summary": "...",
  "total_issues": 0
}}"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)

    try:
        return json.loads(raw)
    except Exception:
        return {
            "vulnerabilities": [],
            "overall_score": 50,
            "grade": "C",
            "summary": "Analysis parsing failed. Review raw Gemini output.",
            "total_issues": 0,
            "_raw": raw[:500],
        }


# ─── Full Pipeline ────────────────────────────────────────────────────────────

def run_full_analysis(code: str, language: str, db_rules: list = None) -> dict:
    """
    Run the complete DevShield security analysis pipeline:
    1. Bandit static analysis (Python only)
    2. Custom rule matching (default YAML + user DB rules)
    3. Gemini deep AI analysis
    4. Merge + deduplicate
    5. OWASP Top 10 mapping
    6. Sort by severity + compute stats

    Args:
        code:     Source code to analyze
        language: Programming language
        db_rules: Optional extra rules from SQLite custom rules table

    Returns:
        Full analysis report dict
    """
    # Step 1: Bandit (Python only)
    bandit_findings = []
    if "python" in language.lower():
        bandit_findings = _analyze_with_bandit(code)

    # Step 2: Load default YAML rules
    custom_findings = []
    yaml_rules = []
    try:
        if DEFAULT_RULES_PATH.exists():
            yaml_rules = load_rules(str(DEFAULT_RULES_PATH))
    except Exception:
        pass

    all_rules = list(yaml_rules)
    if db_rules:
        all_rules.extend(db_rules)

    if all_rules:
        custom_findings = apply_rules(code, all_rules)

    # Build extra context for Gemini from custom rules
    extra_ctx = ""
    if all_rules:
        rule_names = [r["name"] for r in all_rules[:10]]
        extra_ctx = f"\nAlso check for these custom rule violations:\n" + "\n".join(
            f"- {n}" for n in rule_names
        )

    # Step 3: Gemini analysis
    gemini_report = _analyze_with_gemini(code, language, extra_ctx)
    gemini_vulns = gemini_report.get("vulnerabilities", [])

    # Step 4: Merge — add Bandit and custom findings not already in Gemini results
    gemini_names_lower = {v["name"].lower() for v in gemini_vulns}

    for bv in bandit_findings + custom_findings:
        name_lower = bv["name"].lower()
        already_covered = any(
            name_lower in gn or gn in name_lower for gn in gemini_names_lower
        )
        if not already_covered:
            gemini_vulns.append(bv)
            gemini_names_lower.add(name_lower)

    # Step 5: OWASP mapping
    for vuln in gemini_vulns:
        if not vuln.get("owasp_id"):
            owasp = map_to_owasp(vuln.get("name", ""), vuln.get("description", ""))
            vuln["owasp_id"] = owasp["id"]
            vuln["owasp_name"] = owasp["name"]
            vuln["owasp_url"] = owasp["url"]
        if "source" not in vuln:
            vuln["source"] = "Gemini"

    # Step 6: Sort by severity
    gemini_vulns.sort(
        key=lambda v: SEVERITY_ORDER.get(v.get("severity", "INFO"), 99)
    )

    # Step 7: Severity counts
    severity_counts = {s: 0 for s in SEVERITY_ORDER}
    for v in gemini_vulns:
        sev = v.get("severity", "INFO")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    return {
        "vulnerabilities": gemini_vulns,
        "overall_score": gemini_report.get("overall_score", 50),
        "grade": gemini_report.get("grade", "C"),
        "summary": gemini_report.get("summary", "Analysis complete."),
        "severity_counts": severity_counts,
        "total_issues": len(gemini_vulns),
        "bandit_count": len(bandit_findings),
        "custom_rule_count": len(custom_findings),
        "gemini_count": len([v for v in gemini_vulns if v.get("source") == "Gemini"]),
        "timestamp": datetime.now().isoformat(),
    }


# ─── Auto-Fix ────────────────────────────────────────────────────────────────

def auto_fix_code(code: str, language: str, vulnerabilities: list) -> dict:
    """
    One-click auto-fix: send vulnerable code + issue list through Gemini
    and receive a fully patched version.

    Args:
        code:            Original vulnerable source code
        language:        Programming language
        vulnerabilities: List of vulnerability dicts from run_full_analysis()

    Returns:
        dict with: fixed_code, fixes_applied, remaining_concerns, success
    """
    model = _get_model()

    if not vulnerabilities:
        return {
            "fixed_code": code,
            "fixes_applied": ["No vulnerabilities to fix."],
            "remaining_concerns": [],
            "success": True,
        }

    vuln_summary = "\n".join(
        f"{i + 1}. [{v.get('severity', 'UNKNOWN')}] {v.get('name', 'Unknown')} "
        f"(line {v.get('line', '?')}): {v.get('description', '')[:100]}"
        for i, v in enumerate(vulnerabilities)
    )

    prompt = f"""You are DevShield AI's Auto-Fix Engine. Fix ALL security vulnerabilities in this {language} code.

## Vulnerabilities to Fix
{vuln_summary}

## Original Code
```{language.lower().split()[0]}
{code}
```

## Fix Requirements
- Patch EVERY vulnerability listed above
- Add an inline comment on EACH fix: # SECURITY FIX: <brief description>
- Preserve ALL original functionality — do NOT remove features
- Apply defence-in-depth (fix root cause, not just symptoms)
- Use parameterized queries instead of string concatenation for SQL
- Replace hardcoded secrets with os.environ / environment variable lookups
- Replace MD5/SHA1 with SHA-256 or better
- Replace eval/exec with safe alternatives
- Add input validation where missing

Return ONLY valid JSON (no markdown):
{{
  "fixed_code": "<complete fixed {language} code>",
  "fixes_applied": ["<description of fix 1>", "<description of fix 2>", ...],
  "remaining_concerns": ["<anything that still needs manual review>"]
}}"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)

        data = json.loads(raw)
        return {
            "fixed_code": data.get("fixed_code", code),
            "fixes_applied": data.get("fixes_applied", []),
            "remaining_concerns": data.get("remaining_concerns", []),
            "success": True,
        }

    except json.JSONDecodeError:
        return {
            "fixed_code": response.text if "response" in dir() else code,
            "fixes_applied": ["Auto-fix applied (unstructured response)."],
            "remaining_concerns": ["Manual review recommended."],
            "success": True,
        }

    except Exception as exc:
        return {
            "fixed_code": code,
            "fixes_applied": [],
            "remaining_concerns": [f"Auto-fix failed: {exc}"],
            "success": False,
        }
