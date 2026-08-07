import os
import sys
import asyncio
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import settings
from backend.ai.ai_router import AIRouter

async def test_ai():
    print(f"Loaded Gemini Key: {settings.gemini_api_key[:10]}...")
    router = AIRouter()
    try:
        response, tokens, model = await router.route_request("Hello, what is your name?")
        print(f"Response from AI: {response}")
        print(f"Model used: {model}")
    except Exception as e:
        print(f"Error calling AI: {e}")

if __name__ == "__main__":
    asyncio.run(test_ai())
