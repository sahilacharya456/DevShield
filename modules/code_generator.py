"""
DevShield AI — Module 1: Code Generator
Generates production-ready, secure code via Gemini API.
Informed by the self-improving preference learning system.
"""

import json
import re
from datetime import datetime

import google.generativeai as genai

from config.settings import GEMINI_API_KEY, GEMINI_MODEL, APP_OWNER
from utils.preference_learner import load_preferences, build_preference_context

genai.configure(api_key=GEMINI_API_KEY)

_SYSTEM_INSTRUCTION = f"""You are DevShield AI, an elite secure software development assistant.
Your owner is {APP_OWNER}. Your core mission:

1. Generate production-ready code that is clean, well-commented, and secure by default
2. Follow language-specific idioms and best practices
3. Apply defence-in-depth security from the first line
4. Never hardcode credentials, API keys, tokens, or secrets
5. Always validate and sanitize inputs
6. Implement proper error handling without leaking internals
7. Use environment variables for all configuration

You are precise, professional, and security-first. Every output must be production-ready."""


def _get_model() -> genai.GenerativeModel:
    return genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        system_instruction=_SYSTEM_INSTRUCTION,
    )


def generate_code(
    task: str,
    language: str,
    additional_context: str = "",
    use_preferences: bool = True,
) -> dict:
    """
    Generate production-ready code using Gemini API.

    Args:
        task:               Plain-English description of what to build
        language:           Target programming language
        additional_context: Optional extra requirements from user
        use_preferences:    Whether to inject self-learned preferences

    Returns:
        dict with:
            code                 – Generated source code
            confidence_score     – AI self-rated confidence (1–10)
            confidence_reasoning – Why that confidence level
            key_security_features – List of security measures applied
            dependencies         – Required packages/libraries
            tokens_used          – Gemini token count
            timestamp            – ISO timestamp
            success              – bool
            error                – Error message or None
    """
    model = _get_model()

    # Build learned-preference context
    prefs = load_preferences() if use_preferences else {}
    pref_context = build_preference_context(prefs) if use_preferences else "No preferences loaded."

    prompt = f"""Generate production-ready {language} code for the following task.

## Task Description
{task}

## Additional Requirements
{additional_context if additional_context.strip() else "None specified — apply best practices."}

## Learned User Preferences
{pref_context}

## Mandatory Security Standards
- Validate ALL user inputs before processing
- Never hardcode secrets — use environment variables
- Use parameterized queries for all database operations
- Apply principle of least privilege
- Implement defensive error handling (don't expose stack traces)
- Use cryptographically secure random where randomness is needed
- Log security-relevant events (failed auth, invalid input, etc.)
- Add inline comments explaining security-sensitive sections

## Output Format
Return ONLY valid JSON (no markdown fences, no explanation):
{{
  "code": "<complete {language} code with comments>",
  "confidence_score": <integer 1-10>,
  "confidence_reasoning": "<brief explanation>",
  "key_security_features": ["<feature1>", "<feature2>", ...],
  "dependencies": ["<dep1>", "<dep2>", ...]
}}"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip()

        # Strip markdown fences if Gemini wraps despite instructions
        raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
        raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE)
        raw = raw.strip()

        data = json.loads(raw)

        tokens = 0
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            tokens = getattr(response.usage_metadata, "total_token_count", 0)

        return {
            "code": data.get("code", ""),
            "confidence_score": int(data.get("confidence_score", 7)),
            "confidence_reasoning": data.get("confidence_reasoning", ""),
            "key_security_features": data.get("key_security_features", []),
            "dependencies": data.get("dependencies", []),
            "tokens_used": tokens,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "error": None,
        }

    except json.JSONDecodeError:
        # Gemini returned raw code without JSON wrapper — use it directly
        tokens = 0
        try:
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                tokens = getattr(response.usage_metadata, "total_token_count", 0)
        except Exception:
            pass

        return {
            "code": response.text if "response" in dir() else "",
            "confidence_score": 6,
            "confidence_reasoning": "Structured JSON response unavailable; raw code returned.",
            "key_security_features": [],
            "dependencies": [],
            "tokens_used": tokens,
            "timestamp": datetime.now().isoformat(),
            "success": True,
            "error": None,
        }

    except Exception as exc:
        return {
            "code": "",
            "confidence_score": 0,
            "confidence_reasoning": str(exc),
            "key_security_features": [],
            "dependencies": [],
            "tokens_used": 0,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(exc),
        }
