import os
import instructor
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
import structlog
from backend.config import settings

logger = structlog.get_logger("DevShield.AutoFix")

# Pydantic schema guarantees structured output from the LLM
class AutoFixResult(BaseModel):
    fixed_code: str = Field(description="The complete patched source code")
    fixes_applied: List[str] = Field(description="List of specific security fixes applied")
    remaining_concerns: List[str] = Field(description="Any security concerns that still need manual review")
    confidence: int = Field(description="Confidence score from 0 to 100 that the fix is correct and doesn't break functionality")

class AutoFixEngine:
    def __init__(self):
        if settings.gemini_api_key and settings.gemini_api_key != "your_gemini_api_key_here":
            genai.configure(api_key=settings.gemini_api_key)
            self.client = instructor.from_gemini(
                client=genai.GenerativeModel(
                    model_name=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                ),
                mode=instructor.Mode.GEMINI_JSON,
            )
        else:
            self.client = None
            logger.warning("GEMINI_API_KEY not configured. Auto-fix will not work.")

    def generate_fix(self, original_code: str, vulnerabilities: List[dict], context: str = "") -> Optional[AutoFixResult]:
        if not self.client:
            return None

        vuln_summary = "\n".join(
            f"- [{v.get('severity', 'UNKNOWN')}] {v.get('title', 'Unknown')} (line {v.get('line', '?')}): {v.get('description', '')}"
            for v in vulnerabilities
        )

        prompt = f"""You are a Principal Application Security Engineer. Your task is to fix the following code.
        
## Original Code
```
{original_code}
```

## Vulnerabilities to Fix
{vuln_summary}

{context}

## Instructions
1. Apply a secure fix for each vulnerability.
2. Ensure the code remains functionally equivalent.
3. Do not introduce new vulnerabilities.
4. If a vulnerability cannot be fully fixed autonomously, note it in remaining_concerns.

Return the result matching the requested JSON schema.
"""
        try:
            # We use instructor to enforce the schema
            resp = self.client.messages.create(
                messages=[
                    {"role": "user", "content": prompt}
                ],
                response_model=AutoFixResult,
            )
            return resp
        except Exception as e:
            logger.error(f"Auto-fix generation failed: {e}")
            return None

auto_fix_engine = AutoFixEngine()

def run_auto_fix(original_code: str, vulnerabilities: List[dict], context: str = "") -> Optional[dict]:
    result = auto_fix_engine.generate_fix(original_code, vulnerabilities, context)
    if result:
        return result.model_dump()
    return None
