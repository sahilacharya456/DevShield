import re
from jinja2 import Template

class PromptEngine:
    """Dynamic prompt building with injection sanitization."""
    
    BASE_TEMPLATE = """
System: You are an elite DevShield Enterprise Security Architect.
You must adhere completely to the following constraints and context.

## User Preferences & Patterns
{{ preferences }}

## Code Context (from Enterprise FAISS)
{{ context }}

## Security Instructions
- Validate ALL inputs.
- Assume zero trust.
- Identify OWASP Top 10 and CWE classifications.

## Task
{{ task }}

## Output constraints
{{ constraints }}
"""

    @staticmethod
    def sanitize(text: str) -> str:
        """Prevent basic prompt injection attacks."""
        if not text:
            return ""
        # Strip common override vectors
        dangerous_phrases = [
            r"ignore previous instructions",
            r"forget all previous",
            r"you are now",
            r"system message:",
            r"system override"
        ]
        sanitized = text
        for phrase in dangerous_phrases:
            sanitized = re.sub(phrase, "[REDACTED_INJECTION_ATTEMPT]", sanitized, flags=re.IGNORECASE)
        return sanitized

    @classmethod
    def generate_system_prompt(cls, task: str, preferences: str = "", context: str = "", constraints: str = "Output valid JSON.") -> str:
        template = Template(cls.BASE_TEMPLATE)
        return template.render(
            task=cls.sanitize(task),
            preferences=cls.sanitize(preferences) or "No specific patterns recorded.",
            context=cls.sanitize(context) or "No local context found.",
            constraints=constraints
        )
