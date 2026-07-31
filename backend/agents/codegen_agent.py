import re
import json
from backend.ai.ai_router import AIRouter
from backend.ai.prompt_engineer import build_codegen_prompt

class CodeGenAgent:
    def __init__(self):
        self.router = AIRouter()

    def extract_code(self, response_text: str) -> str:
        matches = re.findall(r'```(?:\w+)?\n(.*?)```', response_text, re.DOTALL)
        if matches:
            return matches[0].strip()
        return response_text.strip()

    async def generate(self, task: str, language: str, security_level: str, preferences: dict) -> dict:
        prompt = build_codegen_prompt(task, language, security_level, preferences)
        
        meta_prompt = f"{prompt}\nAlso, append a JSON object at the end with keys 'confidence_score' (0-100) and 'alternative_approaches' (list of strings)"
        
        text, tokens, ai_used = await self.router.route_request(meta_prompt)
        
        code = self.extract_code(text)
        
        confidence = 90
        alternatives = []
        try:
            json_match = re.search(r'(\{.*confidence_score.*\})', text, re.DOTALL | re.IGNORECASE)
            if json_match:
                data = json.loads(json_match.group(1))
                confidence = data.get("confidence_score", 90)
                alternatives = data.get("alternative_approaches", [])
        except Exception:
            pass

        return {
            "code": code,
            "confidence_score": confidence,
            "alternative_approaches": alternatives,
            "token_cost": tokens,
            "ai_used": ai_used
        }
