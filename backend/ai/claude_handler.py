import os
import structlog
from backend.config import settings

logger = structlog.get_logger()

class ClaudeHandler:
    def __init__(self, model_name: str = "claude-3-5-sonnet-latest"):
        self.client = None
        self.model_name = model_name
        try:
            from anthropic import AsyncAnthropic
            if settings.claude_api_key:
                self.client = AsyncAnthropic(api_key=settings.claude_api_key)
        except Exception as e:
            logger.warning(f"Claude SDK unavailable: {e}")

    async def generate_response(self, prompt: str) -> tuple[str, int]:
        if not self.client:
            raise RuntimeError("Claude SDK or CLAUDE_API_KEY is not configured")
        try:
            logger.info("Calling Claude API")
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            text = response.content[0].text
            token_count = response.usage.input_tokens + response.usage.output_tokens
            return text, token_count
        except Exception as e:
            logger.error(f"Claude API Error: {str(e)}")
            raise e
