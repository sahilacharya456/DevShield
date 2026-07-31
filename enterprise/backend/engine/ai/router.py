import json
import asyncio
import logging
import google.generativeai as genai
from groq import AsyncGroq
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type
from app.core.config import settings

# Initialize logging
logger = logging.getLogger("DevShield.AIRouter")

# Initialize clients
try:
    if settings.GEMINI_API_KEY:
        genai.configure(api_key=settings.GEMINI_API_KEY)
except Exception as e:
    logger.warning(f"Failed to configure Gemini: {e}")

groq_client = None
if settings.GROQ_API_KEY:
    try:
        groq_client = AsyncGroq(api_key=settings.GROQ_API_KEY)
    except Exception as e:
        logger.warning(f"Failed to configure Groq: {e}")


class AIRouter:
    """Enterprise-grade Circuit Breaker and Fallback Router for LLM calls."""
    
    @staticmethod
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    async def _call_gemini(prompt: str, json_mode: bool) -> str:
        model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
        if json_mode:
            prompt += "\n\nOutput ONLY valid JSON."
            
        # [FIXED] Architecture Audit Patch: Offloaded synchronous blocking generation call into the asyncio ThreadPoolExecutor 
        # so it no longer blocks the main FastAPI async workers.
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(None, model.generate_content, prompt)
        return response.text

    @staticmethod
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(3),
        reraise=True
    )
    async def _call_groq(prompt: str, json_mode: bool) -> str:
        if not groq_client:
            raise ValueError("Groq client not configured")
            
        kwargs = {
            "messages": [{"role": "user", "content": prompt}],
            "model": settings.GROQ_MODEL,
            "temperature": 0.2
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            prompt += "\n\nOutput ONLY valid JSON. No markdown fences."
            kwargs["messages"][0]["content"] = prompt
            
        response = await groq_client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    @classmethod
    async def generate(cls, prompt: str, json_mode: bool = False) -> str:
        """Route to primary provider with fast-failover to secondary."""
        primary = settings.LLM_PROVIDER
        
        if primary == "gemini":
            try:
                return await cls._call_gemini(prompt, json_mode)
            except Exception as e:
                logger.error(f"Gemini failed: {e}. Orchestrator failing over to Groq.")
                return await cls._call_groq(prompt, json_mode)
        else:
            try:
                return await cls._call_groq(prompt, json_mode)
            except Exception as e:
                logger.error(f"Groq failed: {e}. Orchestrator failing over to Gemini.")
                return await cls._call_gemini(prompt, json_mode)
