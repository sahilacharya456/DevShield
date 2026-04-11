"""
DevShield AI — Custom Rule Engine
Load and apply user-defined YAML security rules on top of Gemini analysis.
"""

import re
from pathlib import Path

try:
    import yaml
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False


# ─── Load Rules ───────────────────────────────────────────────────────────────

def load_rules(yaml_path: str) -> list[dict]:
    """
    Load security rules from a YAML file.

    Args:
        yaml_path: Absolute or relative path to the YAML rules file.

    Returns:
        List of rule dicts with keys: name, pattern, severity, owasp_id, description
    """
    if not _YAML_AVAILABLE:
        return []

    path = Path(yaml_path)
    if not path.exists():
        return []

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    rules = data.get("rules", []) if isinstance(data, dict) else []
    validated = []
    for rule in rules:
        if not isinstance(rule, dict):
            continue
        if "name" not in rule or "pattern" not in rule:
            continue
        validated.append({
            "name": str(rule.get("name", "")),
            "pattern": str(rule.get("pattern", "")),
            "severity": str(rule.get("severity", "MEDIUM")).upper(),
            "owasp_id": str(rule.get("owasp_id", "")),
            "description": str(rule.get("description", "")),
        })
    return validated


def apply_rules(code: str, rules: list[dict]) -> list[dict]:
    """
    Apply custom rules to source code using regex pattern matching.

    Args:
        code:  Source code string
        rules: List of rule dicts from load_rules()

    Returns:
        List of match dicts: {rule_name, line, severity, owasp_id, description, matched_text}
    """
    findings = []
    lines = code.splitlines()

    for rule in rules:
        pattern = rule.get("pattern", "")
        if not pattern:
            continue
        try:
            compiled = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        except re.error:
            # Invalid regex — skip
            continue

        for i, line in enumerate(lines, start=1):
            match = compiled.search(line)
            if match:
                findings.append({
                    "name": rule["name"],
                    "line": i,
                    "severity": rule["severity"],
                    "owasp_id": rule["owasp_id"],
                    "description": rule["description"] or f'Pattern matched: "{pattern}"',
                    "matched_text": match.group(0)[:80],
                    "source": "CustomRule",
                    "confidence": 0.8,
                    "poc": "",
                    "fix_suggestion": f"Review and fix pattern match: {pattern}",
                    "fixed_code_snippet": "",
                    "owasp_name": "",
                    "owasp_url": "",
                })

    return findings
