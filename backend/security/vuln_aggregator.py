import uuid
from backend.security.owasp_mapper import map_to_owasp

def aggregate_vulnerabilities(bandit_results: list, semgrep_results: list, ai_results: list) -> list:
    combined = bandit_results + semgrep_results + ai_results
    final_vulns = []
    
    for v in combined:
        mapping = map_to_owasp(v.get('id', ''), v.get('description', ''))
        
        sev = v.get('severity', 'MEDIUM')
        if sev == "ERROR" or sev == "WARNING":
            sev = "HIGH" if sev == "ERROR" else "MEDIUM"
            
        final_vulns.append({
            "id": str(uuid.uuid4()),
            "title": v.get("title", "Found Issue"),
            "severity": sev.upper() if isinstance(sev, str) else "MEDIUM",
            "description": v.get("description", "No description provided"),
            "cwe_id": mapping["cwe_id"],
            "owasp_top_10": mapping["owasp_top_10"],
            "line_number": v.get("line_number"),
            "remediation": f"Review {mapping['cwe_id']} guidelines to remediate.",
            "proof_of_concept": None
        })
    return final_vulns
