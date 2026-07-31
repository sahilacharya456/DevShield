import json
import aiofiles
from backend.config import settings
import structlog

logger = structlog.get_logger()

class PreferenceManager:
    async def get_preferences(self) -> dict:
        try:
            async with aiofiles.open(settings.preferences_file, mode='r') as f:
                content = await f.read()
                return json.loads(content)
        except FileNotFoundError:
            return {}
        except json.JSONDecodeError:
            return {}

    async def update_preferences(self, new_prefs: dict) -> dict:
        current = await self.get_preferences()
        current.update(new_prefs)
        async with aiofiles.open(settings.preferences_file, mode='w') as f:
            await f.write(json.dumps(current, indent=2))
        return current
