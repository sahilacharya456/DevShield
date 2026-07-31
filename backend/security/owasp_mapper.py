def map_to_owasp(vuln_id: str, description: str) -> dict:
    description_lower = description.lower()
    
    mapping = {
        "owasp_top_10": "A04:2021-Insecure Design",
        "cwe_id": "CWE-200"
    }
    
    if "sql" in description_lower or "injection" in description_lower:
        mapping["owasp_top_10"] = "A03:2021-Injection"
        mapping["cwe_id"] = "CWE-89"
    elif "xss" in description_lower or "cross-site scripting" in description_lower:
        mapping["owasp_top_10"] = "A03:2021-Injection"
        mapping["cwe_id"] = "CWE-79"
    elif "hardcoded" in description_lower or "password" in description_lower or "secret" in description_lower:
        mapping["owasp_top_10"] = "A07:2021-Identification and Authentication Failures"
        mapping["cwe_id"] = "CWE-798"
    
    return mapping
