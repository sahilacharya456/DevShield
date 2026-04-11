"""
DevShield AI — OWASP Top 10 (2021) Mapper
Maps every detected vulnerability to an official OWASP category.
"""

# ─── Full OWASP Top 10 (2021) Database ────────────────────────────────────────

OWASP_TOP_10 = {
    "A01": {
        "id": "A01:2021",
        "name": "Broken Access Control",
        "description": "Restrictions on authenticated users not properly enforced.",
        "url": "https://owasp.org/Top10/A01_2021-Broken_Access_Control/",
        "cwe_ids": [22, 23, 35, 59, 200, 201, 219, 264, 275, 276, 284, 285, 352, 359, 601, 639, 862, 863],
    },
    "A02": {
        "id": "A02:2021",
        "name": "Cryptographic Failures",
        "description": "Failures related to cryptography leading to sensitive data exposure.",
        "url": "https://owasp.org/Top10/A02_2021-Cryptographic_Failures/",
        "cwe_ids": [261, 296, 310, 319, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 335, 338],
    },
    "A03": {
        "id": "A03:2021",
        "name": "Injection",
        "description": "User-supplied data is not validated, filtered, or sanitized.",
        "url": "https://owasp.org/Top10/A03_2021-Injection/",
        "cwe_ids": [20, 74, 75, 77, 78, 79, 80, 83, 87, 88, 89, 90, 91, 93, 94, 95, 96, 97, 98, 99],
    },
    "A04": {
        "id": "A04:2021",
        "name": "Insecure Design",
        "description": "Missing or ineffective control design — a shift-left security concern.",
        "url": "https://owasp.org/Top10/A04_2021-Insecure_Design/",
        "cwe_ids": [73, 183, 209, 213, 235, 256, 257, 266, 269, 280, 311, 312, 313, 316, 419, 430],
    },
    "A05": {
        "id": "A05:2021",
        "name": "Security Misconfiguration",
        "description": "Missing appropriate security hardening across the stack.",
        "url": "https://owasp.org/Top10/A05_2021-Security_Misconfiguration/",
        "cwe_ids": [2, 11, 13, 15, 16, 260, 315, 520, 526, 537, 541, 548, 611, 614, 756, 776, 942],
    },
    "A06": {
        "id": "A06:2021",
        "name": "Vulnerable and Outdated Components",
        "description": "Using components with known vulnerabilities.",
        "url": "https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/",
        "cwe_ids": [1104],
    },
    "A07": {
        "id": "A07:2021",
        "name": "Identification and Authentication Failures",
        "description": "Weaknesses in authentication and session management.",
        "url": "https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/",
        "cwe_ids": [255, 259, 287, 288, 290, 294, 295, 297, 300, 302, 303, 304, 306, 307, 308, 309, 340],
    },
    "A08": {
        "id": "A08:2021",
        "name": "Software and Data Integrity Failures",
        "description": "Code and infrastructure not protected against integrity violations.",
        "url": "https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/",
        "cwe_ids": [345, 353, 426, 494, 502, 565, 784, 829, 830, 915, 916, 917, 1021, 1188],
    },
    "A09": {
        "id": "A09:2021",
        "name": "Security Logging and Monitoring Failures",
        "description": "Insufficient logging, detection, monitoring, and active response.",
        "url": "https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/",
        "cwe_ids": [117, 223, 532, 778],
    },
    "A10": {
        "id": "A10:2021",
        "name": "Server-Side Request Forgery (SSRF)",
        "description": "Web app fetches remote resource without validating user-supplied URL.",
        "url": "https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/",
        "cwe_ids": [918],
    },
}

# ─── Keyword → OWASP Category Map ─────────────────────────────────────────────

_KEYWORD_MAP = {
    # A01 - Broken Access Control
    "path traversal": "A01", "directory traversal": "A01", "broken access": "A01",
    "csrf": "A01", "cross-site request forgery": "A01", "open redirect": "A01",
    "privilege escalation": "A01", "idor": "A01", "insecure direct object": "A01",
    "missing authorization": "A01", "forced browsing": "A01",

    # A02 - Cryptographic Failures
    "md5": "A02", "sha1": "A02", "sha-1": "A02", "des": "A02", "3des": "A02",
    "ecb mode": "A02", "weak crypto": "A02", "insecure crypto": "A02",
    "cleartext": "A02", "plaintext password": "A02", "unencrypted": "A02",
    "sensitive data exposure": "A02", "weak cipher": "A02", "rc4": "A02",
    "deprecated tls": "A02", "ssl 2": "A02", "ssl 3": "A02",

    # A03 - Injection
    "sql injection": "A03", "sqli": "A03", "nosql injection": "A03",
    "command injection": "A03", "os injection": "A03", "shell injection": "A03",
    "xss": "A03", "cross-site scripting": "A03", "xml injection": "A03",
    "xpath injection": "A03", "ldap injection": "A03", "template injection": "A03",
    "ssti": "A03", "code injection": "A03", "eval injection": "A03",
    "injection": "A03",

    # A04 - Insecure Design
    "race condition": "A04", "integer overflow": "A04", "buffer overflow": "A04",
    "insecure design": "A04", "business logic": "A04", "time-of-check": "A04",
    "toctou": "A04",

    # A05 - Security Misconfiguration
    "security misconfiguration": "A05", "debug mode": "A05", "verbose error": "A05",
    "xxe": "A05", "xml external entity": "A05", "default credentials": "A05",
    "default password": "A05", "cors misconfiguration": "A05",
    "unnecessarily enabled": "A05", "stack trace": "A05",

    # A06 - Vulnerable Components
    "outdated": "A06", "deprecated": "A06", "vulnerable component": "A06",
    "known vulnerability": "A06", "outdated library": "A06", "cve": "A06",

    # A07 - Auth Failures
    "hardcoded password": "A07", "hardcoded credential": "A07",
    "hardcoded secret": "A07", "hardcoded api key": "A07", "hardcoded token": "A07",
    "weak password": "A07", "missing authentication": "A07", "broken auth": "A07",
    "session fixation": "A07", "weak session": "A07", "insecure session": "A07",
    "credential": "A07", "password in code": "A07",

    # A08 - Integrity Failures
    "insecure deserialization": "A08", "deserialization": "A08",
    "pickle": "A08", "yaml.load": "A08", "unsafe deserialization": "A08",
    "untrusted data": "A08", "integrity": "A08",

    # A09 - Logging Failures
    "no logging": "A09", "missing logging": "A09", "insufficient logging": "A09",
    "log injection": "A09", "sensitive data in log": "A09",

    # A10 - SSRF
    "ssrf": "A10", "server-side request forgery": "A10",
    "unvalidated url": "A10", "open url": "A10",
}

_UNKNOWN = {
    "id": "A00:2021",
    "name": "Unclassified",
    "description": "Does not map directly to an OWASP Top 10 category.",
    "url": "https://owasp.org/Top10/",
    "cwe_ids": [],
}


# ─── Public API ───────────────────────────────────────────────────────────────

def map_to_owasp(vuln_name: str, description: str = "") -> dict:
    """
    Map a vulnerability name/description to an OWASP Top 10 (2021) category.

    Args:
        vuln_name:   Vulnerability name (e.g. 'SQL Injection')
        description: Optional detailed description for better matching

    Returns:
        dict with id, name, description, url, cwe_ids
    """
    combined = (vuln_name + " " + description).lower()

    for keyword, cat_key in _KEYWORD_MAP.items():
        if keyword in combined:
            entry = OWASP_TOP_10[cat_key].copy()
            return entry

    return _UNKNOWN.copy()


def get_all_categories() -> list[dict]:
    """Return all OWASP Top 10 categories as a list."""
    return list(OWASP_TOP_10.values())


def get_category(cat_key: str) -> dict:
    """Return a specific OWASP category by key (e.g. 'A03')."""
    return OWASP_TOP_10.get(cat_key, _UNKNOWN)
