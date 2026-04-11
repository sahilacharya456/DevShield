"""
DevShield AI — Preference Learner
Self-improvement system that learns from Sahil's feedback over time.
"""

import json
from datetime import datetime
from pathlib import Path

from config.settings import PREFERENCES_FILE, APP_OWNER


# ─── Schema ─────────────────────────────────────────────────────────────────

_DEFAULT_PREFS = {
    "version": 1,
    "owner": APP_OWNER,
    "preferred_languages": {},       # lang -> count
    "anti_patterns": [],             # what NOT to do (from low-rated sessions)
    "coding_patterns": [],           # what works well (from 5-star sessions)
    "security_priorities": [],       # extracted security keywords
    "style_preferences": {},         # task -> feedback text for low-rated
    "total_interactions": 0,
    "last_updated": None,
}


# ─── Load / Save ─────────────────────────────────────────────────────────────

def load_preferences() -> dict:
    """Load saved preferences or return defaults."""
    if PREFERENCES_FILE.exists():
        try:
            with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            # Merge with defaults to handle new keys
            prefs = _DEFAULT_PREFS.copy()
            prefs.update(saved)
            return prefs
        except Exception:
            pass
    return _DEFAULT_PREFS.copy()


def save_preferences(prefs: dict):
    """Persist preferences to disk."""
    prefs["last_updated"] = datetime.now().isoformat()
    with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=2, ensure_ascii=False)


# ─── Learning Engine ──────────────────────────────────────────────────────────

def update_preferences_from_feedback(
    task: str,
    language: str,
    rating: int,
    feedback_text: str,
) -> dict:
    """
    Process user feedback and update preference model.

    Args:
        task:          The task description that was used
        language:      Programming language used
        rating:        1–5 star rating from user
        feedback_text: Free-text feedback

    Returns:
        Updated preferences dict
    """
    prefs = load_preferences()
    prefs["total_interactions"] = prefs.get("total_interactions", 0) + 1

    # Track language usage frequency
    pl = prefs.setdefault("preferred_languages", {})
    pl[language] = pl.get(language, 0) + 1

    # High-rated (4–5) → extract patterns to replicate
    if rating >= 4:
        prefs.setdefault("coding_patterns", []).append({
            "task": task[:120],
            "language": language,
            "rating": rating,
            "timestamp": datetime.now().isoformat(),
        })
        # Keep only last 100 patterns
        prefs["coding_patterns"] = prefs["coding_patterns"][-100:]

    # Low-rated (1–2) → learn what to avoid
    if rating <= 2:
        prefs.setdefault("anti_patterns", []).append({
            "task": task[:120],
            "language": language,
            "reason": feedback_text[:200] if feedback_text else "Low rating",
            "timestamp": datetime.now().isoformat(),
        })
        # Store style preference (task → feedback) for future prompts
        if feedback_text:
            prefs.setdefault("style_preferences", {})[task[:60]] = feedback_text[:200]
        prefs["anti_patterns"] = prefs["anti_patterns"][-50:]

    # Extract security keywords from feedback
    if feedback_text:
        security_keywords = [
            "injection", "xss", "csrf", "authentication", "encryption",
            "validation", "sanitization", "logging", "permissions", "owasp",
            "vulnerability", "exploit", "secure", "safety", "credential",
            "token", "password", "hash", "signature", "certificate",
        ]
        found = [
            word for word in security_keywords
            if word in feedback_text.lower()
        ]
        prefs.setdefault("security_priorities", []).extend(found)
        # Deduplicate and keep last 20
        prefs["security_priorities"] = list(dict.fromkeys(prefs["security_priorities"]))[-20:]

    save_preferences(prefs)
    return prefs


def build_preference_context(prefs: dict) -> str:
    """
    Build a human-readable context string to inject into generation prompts.
    """
    lines = []

    if prefs.get("preferred_languages"):
        top_lang = max(prefs["preferred_languages"], key=prefs["preferred_languages"].get)
        lines.append(f"• {APP_OWNER} most frequently builds in {top_lang}.")

    if len(prefs.get("coding_patterns", [])) > 0:
        lines.append("• Past high-rated sessions favored clean, modular code with thorough error handling.")

    if prefs.get("security_priorities"):
        top_sec = list(dict.fromkeys(prefs["security_priorities"]))[:5]
        lines.append(f"• Security focus areas: {', '.join(top_sec)}.")

    if prefs.get("anti_patterns"):
        last = prefs["anti_patterns"][-1]
        lines.append(f"• Avoid repeating past issue: {last.get('reason', 'N/A')[:100]}")

    if not lines:
        lines.append("• No preferences learned yet — this is an early session.")

    return "\n".join(lines)


def get_readiness_for_fine_tuning() -> dict:
    """Check if enough data exists to fine-tune a smaller model."""
    prefs = load_preferences()
    interactions = prefs.get("total_interactions", 0)
    return {
        "total_interactions": interactions,
        "ready": interactions >= 500,
        "progress_pct": min(100, int((interactions / 500) * 100)),
        "remaining": max(0, 500 - interactions),
    }
