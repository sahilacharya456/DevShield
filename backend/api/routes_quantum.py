from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from backend.security.auth import get_pro_user, get_current_user
from backend.models.orm import User

router = APIRouter()


class QuantumAuditRequest(BaseModel):
    code: str = Field(..., description="Source code to audit for quantum-vulnerable cryptography.")
    filename: str = Field("code.py", description="Optional filename for context in the report.")
    use_ast: bool = Field(False, description="If True, uses deep AST analysis in addition to regex scanning.")


@router.post("/audit", summary="QuantumVault™: PQC Code Audit")
async def quantum_audit(
    payload: QuantumAuditRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **QuantumVault™ — Post-Quantum Cryptography Auditor**

    Scans source code for quantum-vulnerable cryptographic operations:
    - RSA, ECC (ECDSA/ECDH) → Shor's Algorithm threat
    - AES-128, DES, RC4, SHA-1, MD5 → Grover's Algorithm threat

    Returns NIST PQC-compliant migration code snippets (CRYSTALS-Kyber, Dilithium, SHA-3).
    """
    from backend.engine.quantum.pqc_auditor import pqc_auditor

    if payload.use_ast:
        return pqc_auditor.audit_ast(payload.code, payload.filename)
    return pqc_auditor.audit(payload.code, payload.filename)


@router.get("/algorithms", summary="List quantum-vulnerable algorithms")
async def list_vulnerable_algorithms(
    current_user: User = Depends(get_current_user)
):
    """
    Returns a list of all cryptographic algorithms flagged as quantum-vulnerable
    with their NIST PQC replacement recommendations.
    """
    from backend.engine.quantum.pqc_auditor import PQC_REPLACEMENTS, VULN_PATTERNS
    return {
        "vulnerable_algorithms": [
            {
                "algo": p["algo"],
                "title": p["title"],
                "severity": p["severity"],
                "cwe": p["cwe"],
                "quantum_threat": "Shor's Algorithm" if p["algo"] in ["RSA", "ECC"] else "Grover's Algorithm",
                "nist_replacement": PQC_REPLACEMENTS.get(p["algo"], {}).get("replacement", ""),
                "migration_library": PQC_REPLACEMENTS.get(p["algo"], {}).get("library", ""),
            }
            for p in VULN_PATTERNS
        ],
        "nist_standard": "NIST SP 800-227 IPD (Post-Quantum Cryptography)",
        "pqc_standards": ["ML-KEM (CRYSTALS-Kyber)", "ML-DSA (CRYSTALS-Dilithium)", "SLH-DSA (SPHINCS+)"]
    }
