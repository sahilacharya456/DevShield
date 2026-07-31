import json
import aiofiles
import asyncio
from backend.config import settings
import structlog

logger = structlog.get_logger()

class FeedbackStore:
    def __init__(self):
        self.lock = asyncio.Lock()
        
    async def log_feedback(self, data: dict):
        async with self.lock:
            async with aiofiles.open(settings.feedback_file, mode='a') as f:
                await f.write(json.dumps(data) + "\n")
