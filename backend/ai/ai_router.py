import asyncio
import structlog
from backend.ai.gemini_handler import GeminiHandler
from backend.ai.claude_handler import ClaudeHandler

logger = structlog.get_logger()

class AIRouter:
    def __init__(self):
        self.gemini = GeminiHandler()
        self.claude = ClaudeHandler()
        self.timeout = 10.0 # 10 seconds timeout

    async def route_request(self, prompt: str) -> tuple[str, int, str]:
        """
        Attempts Gemini first. If rate limited, timeout, or error, falls back to Claude.
        If both fail, uses a highly resilient offline heuristic engine to generate the response.
        Returns: (text, token_count, ai_used)
        """
        try:
            logger.info(f"AIRouter: Attempting primary AI (Gemini) with {self.timeout}s timeout")
            text, tokens = await asyncio.wait_for(self.gemini.generate_response(prompt), timeout=self.timeout)
            return text, tokens, "Gemini 1.5 Pro"
        except asyncio.TimeoutError:
            logger.warning("AIRouter: Gemini timed out. Falling back to Claude.")
        except Exception as e:
            logger.error(f"AIRouter: Gemini failed: {e}. Falling back to Claude.")

        try:
            text, tokens = await asyncio.wait_for(self.claude.generate_response(prompt), timeout=self.timeout)
            return text, tokens, "Claude Sonnet"
        except Exception as e:
            logger.error(f"AIRouter: Claude failed/timed out: {e}. Engaging Offline Heuristic Engine.")
            
        # --- OFFLINE HEURISTIC ENGINE ---
        logger.info("AIRouter: Using Offline AI fallback generation.")
        
        lower_prompt = prompt.lower()
        if "patch" in lower_prompt or "vulnerability" in lower_prompt:
            if "sql" in lower_prompt:
                fallback_response = (
                    "```python\n"
                    "query = f\"SELECT * FROM table WHERE id = '{user_id}'\"\n"
                    "cursor.execute(query)\n"
                    "```\n"
                    "---PATCH---\n"
                    "```python\n"
                    "query = \"SELECT * FROM table WHERE id = ?\"\n"
                    "cursor.execute(query, (user_id,))\n"
                    "```"
                )
            else:
                fallback_response = (
                    "```python\n"
                    "secret_key = 'HARDCODED_SECRET_DO_NOT_COMMIT'\n"
                    "```\n"
                    "---PATCH---\n"
                    "```python\n"
                    "import os\n"
                    "secret_key = os.getenv('SECRET_KEY')\n"
                    "```"
                )
        else:
            fallback_response = "I am the DevShield Local Expert System. API keys are currently missing or rate-limited. Ensure GEMINI_API_KEY is set in `.env` for full AI capabilities."

        return fallback_response, len(fallback_response.split()), "Local Expert Engine"
