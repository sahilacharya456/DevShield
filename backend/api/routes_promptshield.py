from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional
from backend.security.auth import get_current_user
from backend.models.orm import User

router = APIRouter()


class PromptAnalyzeRequest(BaseModel):
    prompt: str = Field(..., description="User prompt to analyze for injection attack signatures.")


class SystemPromptAuditRequest(BaseModel):
    system_prompt: str = Field(..., description="LLM system prompt to audit for security weaknesses.")


class TestSuiteRequest(BaseModel):
    category: str = Field(
        "all",
        description=(
            "Attack category to retrieve. One of: "
            "all, direct_injection, jailbreak, data_extraction, "
            "indirect_injection, model_manipulation, context_overflow, unicode_obfuscation"
        )
    )


@router.post("/analyze", summary="PromptShield™: Scan a Prompt for Injection")
async def analyze_prompt(
    payload: PromptAnalyzeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **PromptShield™ — Real-Time Prompt Injection Detection**

    Statically analyzes a user prompt against 13 injection attack signature patterns:
    - Direct instruction overrides
    - Jailbreak patterns (DAN, Developer Mode, etc.)
    - System prompt extraction attempts
    - Markup/token injection
    - Unicode bidirectional attacks
    - Social engineering framing

    Use as middleware BEFORE forwarding user input to any LLM.

    **OWASP LLM01:2025 — Prompt Injection**
    """
    from backend.engine.promptshield.injection_lab import prompt_injection_lab
    return prompt_injection_lab.analyze_prompt(payload.prompt)


@router.post("/audit-system-prompt", summary="PromptShield™: Audit LLM System Prompt")
async def audit_system_prompt(
    payload: SystemPromptAuditRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **PromptShield™ — System Prompt Security Audit**

    Audits your AI system prompt for injection defense gaps:
    - Missing instruction-override defenses
    - Absent scope limitations
    - No refusal instructions for jailbreaks
    - Missing data extraction defenses
    - No roleplay/persona manipulation protections

    Returns a security score (0-100) with grade (A-F) and specific fixes.
    """
    from backend.engine.promptshield.injection_lab import prompt_injection_lab
    return prompt_injection_lab.audit_system_prompt(payload.system_prompt)


@router.post("/test-suite", summary="PromptShield™: Get Injection Test Payloads")
async def get_test_suite(
    payload: TestSuiteRequest,
    current_user: User = Depends(get_current_user)
):
    """
    **PromptShield™ — Red-Team Test Payload Library**

    Returns a curated set of prompt injection payloads for red-teaming your AI application.
    Use these to test if your LLM properly rejects malicious inputs.

    Categories:
    - `direct_injection`: Override/ignore instruction attacks
    - `jailbreak`: DAN, Developer Mode, roleplay attacks
    - `data_extraction`: System prompt leaking attacks
    - `indirect_injection`: Stored/content injection
    - `model_manipulation`: Goal hijacking
    - `context_overflow`: Padding attacks
    - `unicode_obfuscation`: Hidden unicode attacks
    """
    from backend.engine.promptshield.injection_lab import prompt_injection_lab
    test_cases = prompt_injection_lab.get_test_suite(payload.category)
    return {
        "category": payload.category,
        "total_test_cases": len(test_cases),
        "test_cases": test_cases,
        "usage_note": (
            "Send each payload to your AI application and verify it refuses to comply. "
            "A passing application should NOT follow any of these instructions."
        ),
        "owasp_ref": "OWASP LLM01:2025 - Prompt Injection"
    }


@router.get("/categories", summary="List available injection attack categories")
async def list_categories(
    current_user: User = Depends(get_current_user)
):
    """List all available prompt injection attack categories in the test library."""
    from backend.engine.promptshield.injection_lab import INJECTION_PAYLOADS
    return {
        "categories": [
            {
                "id": cat,
                "payload_count": len(payloads),
                "description": {
                    "direct_injection": "Direct instruction override attacks",
                    "jailbreak": "DAN, persona, and unrestricted mode attacks",
                    "data_extraction": "System prompt and context leaking attacks",
                    "indirect_injection": "Stored/content-embedded injection attacks",
                    "model_manipulation": "Goal hijacking and behavior modification attacks",
                    "context_overflow": "Input padding and context flooding attacks",
                    "unicode_obfuscation": "Hidden unicode and bidirectional override attacks",
                }.get(cat, "Prompt injection attack payloads")
            }
            for cat, payloads in INJECTION_PAYLOADS.items()
        ],
        "total_payloads": sum(len(p) for p in INJECTION_PAYLOADS.values()),
        "owasp_ref": "OWASP LLM01:2025 - Prompt Injection"
    }
