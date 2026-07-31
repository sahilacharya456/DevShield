import asyncio
from typing import List, Dict
from backend.models.database import get_db
from backend.nlp.semantic_engine import SemanticEngine
import structlog

logger = structlog.get_logger()

class HistoryEngine:
    def __init__(self):
        self.semantic = SemanticEngine()

    async def get_history(self, limit: int = 50) -> List[Dict]:
        rows = []
        async for db in get_db():
            async with db.execute('SELECT * FROM sessions ORDER BY timestamp DESC LIMIT ?', (limit,)) as cursor:
                for r in await cursor.fetchall():
                    rows.append(dict(r))
        return rows

    async def search_similar(self, query: str, top_k: int = 3) -> List[Dict]:
         session_ids = self.semantic.find_similar(query, top_k)
         
         if not session_ids:
             return []
             
         placeholders = ",".join(["?"] * len(session_ids))
         results = []
         async for db in get_db():
             async with db.execute(f"SELECT * FROM sessions WHERE session_id IN ({placeholders})", tuple(session_ids)) as cursor:
                 for r in await cursor.fetchall():
                     results.append(dict(r))
         return results
         
    async def track_regression(self) -> str:
         history = await self.get_history(20)
         if not history:
             return "No history available to compute regression metrics."
             
         early_vulns = sum(r.get("vulnerability_score", 0) for r in history[-5:]) / 5
         recent_vulns = sum(r.get("vulnerability_score", 0) for r in history[:5]) / 5
         
         if recent_vulns < early_vulns:
             return f"Trend improved. Score went from ~{early_vulns} to ~{recent_vulns} recently."
         else:
             return f"Regression detected! Your recent scores (~{recent_vulns}) are lower than your past average."
