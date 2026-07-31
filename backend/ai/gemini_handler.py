import os
import structlog
from backend.config import settings

logger = structlog.get_logger()

class GeminiHandler:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        self.model = None
        self.model_name = model_name
        try:
            import google.generativeai as genai
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            logger.warning(f"Gemini SDK unavailable: {e}")

    async def generate_response(self, prompt: str) -> tuple[str, int]:
        if not self.model:
            raise RuntimeError("Gemini SDK or GEMINI_API_KEY is not configured")
        try:
            logger.info("Calling Gemini API")
            # Generate content async
            response = await self.model.generate_content_async(prompt)
            # Estimate tokens
            token_count = self.model.count_tokens(prompt).total_tokens + self.model.count_tokens(response.text).total_tokens
            return response.text, token_count
        except Exception as e:
            logger.error(f"Gemini API Error: {str(e)}")
            raise e
