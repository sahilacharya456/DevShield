import structlog
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = structlog.get_logger("DevShield.AttackPath")

# ---------------------------------------------------------------------------
# MITRE ATT&CK® Framework — Technique Mappings
# ---------------------------------------------------------------------------
MITRE_MAPPINGS: Dict[str, Dict[str, Any]] = {
    "SQL Injection Risk": {
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "technique": "T1190 — Exploit Public-Facing Application",
        "technique_id": "T1190",
        "next_steps": ["Credential Dumping via DB", "Privilege Escalation via xp_cmdshell", "Data Exfiltration"],
        "impact": "Complete database compromise, authentication bypass, potential OS-level RCE via xp_cmdshell"
    },
    "Command Injection Risk": {
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "technique": "T1059 — Command and Scripting Interpreter",
        "technique_id": "T1059",
        "next_steps": ["Establish Persistence", "Lateral Movement", "Ransomware Deployment"],
        "impact": "Full Remote Code Execution (RCE) on application server"
    },
    "Insecure Deserialization": {
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "technique": "T1059.006 — Python/Pickle Deserialization RCE",
        "technique_id": "T1059.006",
        "next_steps": ["Remote Code Execution", "Container Escape", "Host Compromise"],
        "impact": "Arbitrary code execution during deserialization phase"
    },
    "Hardcoded Cryptographic Secret": {
        "tactic": "Credential Access",
        "tactic_id": "TA0006",
        "technique": "T1552.001 — Credentials in Files",
        "technique_id": "T1552.001",
        "next_steps": ["Cloud Account Takeover", "API Abuse", "Lateral Movement", "Data Exfiltration"],
        "impact": "Attacker gains persistent access to all services using the exposed credential"
    },
    "Malicious DGA Domain": {
        "tactic": "Command and Control",
        "tactic_id": "TA0011",
        "technique": "T1568.002 — Dynamic Resolution: Domain Generation Algorithms",
        "technique_id": "T1568.002",
        "next_steps": ["Data Exfiltration via DNS", "C2 Beaconing", "Malware Delivery"],
        "impact": "Covert communication channel to attacker-controlled C2 infrastructure"
    },
    "Path Traversal Risk": {
        "tactic": "Discovery",
        "tactic_id": "TA0007",
        "technique": "T1083 — File and Directory Discovery",
        "technique_id": "T1083",
        "next_steps": ["Sensitive File Access", "Configuration File Theft", "Credential Discovery"],
        "impact": "Access to arbitrary files outside web root, including /etc/passwd, config files, SSH keys"
    },
    "Server-Side Template Injection": {
        "tactic": "Execution",
        "tactic_id": "TA0002",
        "technique": "T1059 — Template Engine Code Execution",
        "technique_id": "T1059",
        "next_steps": ["Remote Code Execution", "Data Exfiltration", "Server Takeover"],
        "impact": "Full RCE via template engine sandbox escape (Jinja2/Twig/Pebble)"
    },
    "XML External Entity (XXE)": {
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "technique": "T1190 — XXE via XML Parser",
        "technique_id": "T1190",
        "next_steps": ["SSRF", "Internal Network Scanning", "Credential File Access"],
        "impact": "Server-Side Request Forgery, local file disclosure, internal service enumeration"
    },
    "Open Redirect": {
        "tactic": "Initial Access",
        "tactic_id": "TA0001",
        "technique": "T1566.002 — Spear Phishing Link",
        "technique_id": "T1566.002",
        "next_steps": ["Credential Phishing", "OAuth Token Theft", "Account Compromise"],
        "impact": "Enables trusted-domain phishing attacks. Can bypass OAuth redirect validation."
    },
    "Insecure Direct Object Reference": {
        "tactic": "Collection",
        "tactic_id": "TA0009",
        "technique": "T1530 — Data from Cloud Storage Object",
        "technique_id": "T1530",
        "next_steps": ["Unauthorized Data Access", "PII Exfiltration", "Mass Account Enumeration"],
        "impact": "Access to other users' private data without authorization (BOLA/IDOR)"
    },
}

# Default MITRE mapping for unmapped vulnerability types
DEFAULT_MITRE = {
    "tactic": "Exploitation",
    "tactic_id": "TA0002",
    "technique": "T1203 — Exploitation for Client Execution",
    "technique_id": "T1203",
    "next_steps": ["Code Execution", "Further Exploitation"],
    "impact": "Impact requires manual security analysis — potential code execution or data exposure."
}

# Lockheed Martin Cyber Kill Chain® phases
KILL_CHAIN_PHASES = [
    "Reconnaissance",
    "Weaponization",
    "Delivery",
    "Exploitation",
    "Installation",
    "Command & Control",
    "Actions on Objective"
]

TACTIC_TO_KILL_CHAIN = {
    "Reconnaissance": "Reconnaissance",
    "Resource Development": "Weaponization",
    "Initial Access": "Delivery",
    "Execution": "Exploitation",
    "Persistence": "Installation",
    "Privilege Escalation": "Installation",
    "Defense Evasion": "Installation",
    "Credential Access": "Exploitation",
    "Discovery": "Reconnaissance",
    "Lateral Movement": "Actions on Objective",
    "Collection": "Actions on Objective",
    "Command and Control": "Command & Control",
    "Exfiltration": "Actions on Objective",
    "Impact": "Actions on Objective",
    "Exploitation": "Exploitation",  # fallback
}

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


class AttackPathSynthesizer:
    """
    AttackPath™ — AI Autonomous Kill-Chain Generator.

    Given a set of vulnerabilities (e.g., from SAST, SCA, or PQC audit output),
    automatically constructs the most likely attacker kill-chain:

        Entry Point → Lateral Movement → Privilege Escalation → Exfiltrate/Impact

    Maps to both:
    - Lockheed Martin Cyber Kill Chain® (7 phases)
    - MITRE ATT&CK® Framework (tactics + techniques)
    """

    def synthesize(
        self,
        vulnerabilities: List[Dict[str, Any]],
        project_name: str = "Target Application",
        attacker_profile: str = "APT"
    ) -> Dict[str, Any]:
        """
        Build a complete attack kill-chain from a vulnerability list.

        Args:
            vulnerabilities: List of finding dicts (must have 'title', 'severity', 'line').
            project_name: Name of the target project/service.
            attacker_profile: Threat actor profile ('APT', 'Ransomware', 'Insider', 'Script Kiddie').

        Returns:
            Full attack path with MITRE ATT&CK mapping, kill-chain, narrative, and risk scoring.
        """
        if not vulnerabilities:
            return {
                "project": project_name,
                "attack_path": [],
                "kill_chain_coverage": {phase: [] for phase in KILL_CHAIN_PHASES},
                "overall_risk": "LOW",
                "summary": "No vulnerabilities provided. Cannot synthesize attack path.",
                "synthesized_at": datetime.now(timezone.utc).isoformat(),
            }

        attack_steps = []
        entry_points = []
        pivots = []
        objectives = []

        for vuln in vulnerabilities:
            title = vuln.get("title", "Unknown Vulnerability")
            severity = vuln.get("severity", "LOW")
            mitre_info = MITRE_MAPPINGS.get(title, DEFAULT_MITRE)

            tactic = mitre_info.get("tactic", "Exploitation")

            step = {
                "step_id": len(attack_steps) + 1,
                "vulnerability": title,
                "severity": severity,
                "tactic": tactic,
                "tactic_id": mitre_info.get("tactic_id", "TA0002"),
                "technique": mitre_info.get("technique", DEFAULT_MITRE["technique"]),
                "technique_id": mitre_info.get("technique_id", "T1203"),
                "description": (
                    f"Attacker exploits '{title}' ({severity}) to achieve "
                    f"{tactic.lower()} capability."
                ),
                "impact": mitre_info.get("impact", "Unknown impact — manual analysis required."),
                "next_steps": mitre_info.get("next_steps", ["Further exploitation"]),
                "source_line": vuln.get("line", 0),
                "source_file": vuln.get("filename", ""),
                "kill_chain_phase": TACTIC_TO_KILL_CHAIN.get(tactic, "Exploitation"),
                "attacker_value": self._score_attacker_value(severity, tactic, mitre_info),
            }
            attack_steps.append(step)

            # Classify into kill-chain roles
            if tactic in ["Initial Access", "Credential Access"]:
                entry_points.append(title)
            elif tactic in ["Execution", "Persistence", "Privilege Escalation", "Defense Evasion"]:
                pivots.append(title)
            elif tactic in ["Command and Control", "Exfiltration", "Impact", "Collection"]:
                objectives.append(title)

        # Sort by severity (CRITICAL first), then by attacker value
        attack_steps.sort(
            key=lambda x: (SEVERITY_ORDER.get(x["severity"], 4), -x.get("attacker_value", 0))
        )

        # Re-number steps after sort
        for i, step in enumerate(attack_steps, 1):
            step["step_id"] = i

        # Risk assessment
        critical_steps = [s for s in attack_steps if s["severity"] == "CRITICAL"]
        high_steps = [s for s in attack_steps if s["severity"] == "HIGH"]

        if critical_steps:
            overall_risk = "CRITICAL"
        elif high_steps:
            overall_risk = "HIGH"
        elif attack_steps:
            overall_risk = "MEDIUM"
        else:
            overall_risk = "LOW"

        # Estimated time to breach (attacker capability model)
        time_to_breach = self._estimate_ttp(
            critical_count=len(critical_steps),
            attacker_profile=attacker_profile
        )

        return {
            "project": project_name,
            "attacker_profile": attacker_profile,
            "overall_risk": overall_risk,
            "total_attack_vectors": len(attack_steps),
            "entry_points": entry_points or ["No clear entry point identified"],
            "pivot_opportunities": pivots,
            "attacker_objectives": objectives or ["Data Exfiltration", "Ransomware Deployment"],
            "estimated_time_to_breach": time_to_breach,
            "attack_steps": attack_steps,
            "kill_chain_coverage": self._map_to_kill_chain(attack_steps),
            "narrative": self._build_narrative(attack_steps, project_name, attacker_profile),
            "executive_summary": self._build_executive_summary(
                project_name, attack_steps, entry_points,
                critical_steps, time_to_breach, attacker_profile
            ),
            "mitre_tactics_used": list({s["tactic"] for s in attack_steps}),
            "mitre_techniques_used": list({s["technique_id"] for s in attack_steps}),
            "synthesized_at": datetime.now(timezone.utc).isoformat(),
        }

    def _score_attacker_value(
        self, severity: str, tactic: str, mitre_info: Dict[str, Any]
    ) -> int:
        """Score the strategic value of a vulnerability to an attacker (0-100)."""
        base = {"CRITICAL": 80, "HIGH": 60, "MEDIUM": 40, "LOW": 20}.get(severity, 10)
        # Boost for high-value tactics
        tactic_boost = {
            "Initial Access": 15,
            "Credential Access": 15,
            "Command and Control": 10,
            "Exfiltration": 10,
            "Execution": 5,
        }.get(tactic, 0)
        # Boost for multi-step exploitation chains
        chain_depth = len(mitre_info.get("next_steps", []))
        chain_boost = min(10, chain_depth * 3)
        return min(100, base + tactic_boost + chain_boost)

    def _map_to_kill_chain(self, steps: List[Dict]) -> Dict[str, List[str]]:
        """Map attack steps to Lockheed Martin Cyber Kill Chain® phases."""
        phase_mapping: Dict[str, List[str]] = {phase: [] for phase in KILL_CHAIN_PHASES}
        # Pre-populate with always-present attacker activities
        phase_mapping["Reconnaissance"] = ["OSINT gathering", "Port scanning", "Technology fingerprinting"]
        phase_mapping["Weaponization"] = ["Exploit framework selection", "Payload crafting"]
        phase_mapping["Actions on Objective"] = ["Data exfiltration", "Ransomware deployment", "Persistence establishment"]

        for step in steps:
            phase = step.get("kill_chain_phase", "Exploitation")
            if phase in phase_mapping:
                entry = f"{step['vulnerability']} ({step['severity']})"
                if entry not in phase_mapping[phase]:
                    phase_mapping[phase].append(entry)

        return phase_mapping

    def _build_narrative(
        self, steps: List[Dict], project: str, attacker_profile: str
    ) -> str:
        """Build a human-readable attack narrative for the security report."""
        if not steps:
            return "No attack path synthesized."

        profile_descriptions = {
            "APT": "A nation-state Advanced Persistent Threat (APT) actor",
            "Ransomware": "A financially-motivated ransomware threat group",
            "Insider": "A malicious insider with privileged access",
            "Script Kiddie": "An opportunistic attacker using automated exploit tools",
        }
        actor_desc = profile_descriptions.get(attacker_profile, "A sophisticated threat actor")

        narrative_parts = [
            f"## Attack Narrative: '{project}'\n",
            f"**Threat Actor Profile:** {actor_desc}\n\n",
            f"{actor_desc} targeting '{project}' would execute the following kill-chain:\n\n"
        ]

        for step in steps[:6]:  # Top 6 most critical steps
            narrative_parts.append(
                f"### Step {step['step_id']}: {step['tactic']} — {step['technique_id']}\n"
                f"**Vulnerability:** {step['vulnerability']} ({step['severity']})\n"
                f"**Action:** {step['description']}\n"
                f"**Impact:** {step['impact']}\n"
                f"**Enables:** {', '.join(step['next_steps'][:3])}\n\n"
            )

        if len(steps) > 6:
            narrative_parts.append(
                f"_...and {len(steps) - 6} additional attack vectors not shown._\n"
            )

        return "".join(narrative_parts)

    def _build_executive_summary(
        self,
        project: str,
        steps: List[Dict],
        entry_points: List[str],
        critical_steps: List[Dict],
        time_to_breach: str,
        attacker_profile: str
    ) -> str:
        """Build a concise executive-level summary."""
        primary_entry = entry_points[0] if entry_points else "an unknown vulnerability"
        return (
            f"A {attacker_profile}-level attacker can achieve full system compromise of "
            f"'{project}' by chaining {len(steps)} discovered vulnerabilities. "
            f"Primary entry point: {primary_entry}. "
            f"{'CRITICAL-severity vulnerabilities present. ' if critical_steps else ''}"
            f"Estimated time to breach: {time_to_breach}. "
            f"Immediate remediation of all CRITICAL and HIGH findings is strongly recommended."
        )

    def _estimate_ttp(self, critical_count: int, attacker_profile: str) -> str:
        """Estimate time-to-breach based on vulnerability severity and attacker sophistication."""
        profile_multipliers = {
            "APT": 0.5,          # Nation-state: very fast
            "Ransomware": 0.7,   # Ransomware groups: fast
            "Insider": 0.3,      # Already inside: extremely fast
            "Script Kiddie": 2.0  # Automated tools: slower but persistent
        }
        multiplier = profile_multipliers.get(attacker_profile, 1.0)

        if critical_count >= 3:
            base_hours = 0.5 * multiplier
        elif critical_count >= 1:
            base_hours = 2.0 * multiplier
        else:
            base_hours = 8.0 * multiplier

        if base_hours < 1:
            return "< 30 minutes"
        elif base_hours < 2:
            return "< 1 hour"
        elif base_hours < 4:
            return "1-4 hours"
        elif base_hours < 24:
            return f"~{int(base_hours)} hours"
        else:
            return f"~{int(base_hours / 24)} days"

    def synthesize_from_sast(
        self, code: str, project_name: str = "Target Application"
    ) -> Dict[str, Any]:
        """
        Convenience method: runs SAST analysis on code, then synthesizes the kill-chain.
        Integrates with the existing SAST tree-sitter analyzer.
        """
        try:
            from backend.engine.sast.tree_sitter_analyzer import run_sast
            sast_results = run_sast(code)
            vulnerabilities = sast_results.get("findings", [])
        except Exception as e:
            logger.error("sast_integration_failed", error=str(e))
            vulnerabilities = []

        return self.synthesize(vulnerabilities, project_name)


# Module-level singleton
attack_path_synthesizer = AttackPathSynthesizer()
