from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from backend.security.auth import get_current_user
from backend.models.orm import User

router = APIRouter()


class SynthesizeRequest(BaseModel):
    vulnerabilities: List[Dict[str, Any]] = Field(
        ...,
        description=(
            "List of vulnerability findings. Each must have 'title' and 'severity'. "
            "Optional: 'line', 'filename'. "
            "Compatible with SAST, SCA, and PQC audit output formats."
        )
    )
    project_name: str = Field("Target Application", description="Name of the target application.")
    attacker_profile: str = Field(
        "APT",
        description="Threat actor profile: APT | Ransomware | Insider | Script Kiddie"
    )


class SastSynthesizeRequest(BaseModel):
    code: str = Field(..., description="Source code to SAST-scan and synthesize an attack path for.")
    project_name: str = Field("Target Application", description="Project name for the report.")
    attacker_profile: str = Field("APT", description="Threat actor profile.")


@router.post("/synthesize", summary="AttackPath™: Synthesize Kill-Chain from Vulnerabilities")
async def synthesize_attack_path(
    payload: SynthesizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **AttackPath™ — AI Kill-Chain Synthesizer**

    Takes a list of vulnerabilities and constructs the most likely attacker kill-chain,
    mapping each finding to:
    - **MITRE ATT&CK®** tactic + technique (e.g., T1190, T1059)
    - **Lockheed Martin Kill Chain®** phase (Reconnaissance → Actions on Objective)
    - **Attacker objective** (Data Exfiltration, Ransomware, Persistence)

    Returns a full attack narrative, executive summary, and time-to-breach estimate.
    Supports attacker profiles: APT, Ransomware, Insider, Script Kiddie.
    """
    from backend.engine.killchain.attack_path_synthesizer import attack_path_synthesizer

    if not payload.vulnerabilities:
        raise HTTPException(status_code=400, detail="At least one vulnerability is required.")

    if payload.attacker_profile not in ["APT", "Ransomware", "Insider", "Script Kiddie"]:
        raise HTTPException(
            status_code=400,
            detail="attacker_profile must be one of: APT, Ransomware, Insider, Script Kiddie"
        )

    return attack_path_synthesizer.synthesize(
        vulnerabilities=payload.vulnerabilities,
        project_name=payload.project_name,
        attacker_profile=payload.attacker_profile
    )


@router.post("/synthesize-from-code", summary="AttackPath™: SAST Scan + Kill-Chain in One Step")
async def synthesize_from_code(
    payload: SastSynthesizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **AttackPath™ — Auto SAST + Kill-Chain**

    Convenience endpoint that:
    1. Runs SAST analysis on the provided code
    2. Automatically synthesizes the kill-chain from discovered vulnerabilities

    Returns both the raw SAST findings AND the full attack path synthesis in one call.
    """
    from backend.engine.killchain.attack_path_synthesizer import attack_path_synthesizer
    from backend.engine.sast.tree_sitter_analyzer import run_sast

    try:
        sast_results = run_sast(payload.code)
        vulnerabilities = sast_results.get("findings", [])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SAST analysis failed: {str(e)}")

    kill_chain = attack_path_synthesizer.synthesize(
        vulnerabilities=vulnerabilities,
        project_name=payload.project_name,
        attacker_profile=payload.attacker_profile
    )

    return {
        "sast_findings": sast_results,
        "kill_chain": kill_chain,
        "pipeline": "SAST → AttackPath™ Kill-Chain Synthesis"
    }


@router.get("/mitre-mappings", summary="AttackPath™: View MITRE ATT&CK Mappings")
async def get_mitre_mappings(
    current_user: User = Depends(get_current_user)
):
    """
    Returns all MITRE ATT&CK® technique mappings used by the AttackPath™ engine.
    Useful for understanding how vulnerabilities translate to attacker tactics.
    """
    from backend.engine.killchain.attack_path_synthesizer import MITRE_MAPPINGS, KILL_CHAIN_PHASES
    return {
        "total_mappings": len(MITRE_MAPPINGS),
        "kill_chain_phases": KILL_CHAIN_PHASES,
        "mappings": {
            vuln_type: {
                "tactic": info["tactic"],
                "tactic_id": info.get("tactic_id", ""),
                "technique": info["technique"],
                "technique_id": info.get("technique_id", ""),
                "next_steps": info["next_steps"],
                "impact": info["impact"],
            }
            for vuln_type, info in MITRE_MAPPINGS.items()
        },
        "framework": "MITRE ATT&CK® v14",
        "kill_chain_framework": "Lockheed Martin Cyber Kill Chain®"
    }


@router.get("/attacker-profiles", summary="AttackPath™: View Attacker Profiles")
async def get_attacker_profiles(
    current_user: User = Depends(get_current_user)
):
    """Returns available threat actor profiles and their breach time multipliers."""
    return {
        "profiles": [
            {
                "id": "APT",
                "name": "Advanced Persistent Threat (Nation-State)",
                "description": "Highly sophisticated, patient, well-resourced. Focuses on stealth and long-term access.",
                "time_multiplier": 0.5,
                "typical_objectives": ["Espionage", "IP Theft", "Long-term persistence"]
            },
            {
                "id": "Ransomware",
                "name": "Ransomware Threat Group",
                "description": "Financially motivated, moves fast, deploys double-extortion tactics.",
                "time_multiplier": 0.7,
                "typical_objectives": ["Data encryption", "Data exfiltration", "Extortion"]
            },
            {
                "id": "Insider",
                "name": "Malicious Insider",
                "description": "Already has legitimate access. Can move extremely quickly without detection.",
                "time_multiplier": 0.3,
                "typical_objectives": ["Data theft", "Sabotage", "Credential abuse"]
            },
            {
                "id": "Script Kiddie",
                "name": "Opportunistic Attacker",
                "description": "Uses automated tools and publicly available exploits. Less targeted but persistent.",
                "time_multiplier": 2.0,
                "typical_objectives": ["Cryptomining", "Botnet recruitment", "Defacement"]
            },
        ]
    }
