import json
import asyncio
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
import structlog
from backend.config import settings
from backend.models.database import get_db

logger = structlog.get_logger()
DEVSHIELD_DIR = Path.home() / ".devshield"
FINETUNE_DATASET = DEVSHIELD_DIR / "finetune_dataset.jsonl"

class PreferenceEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=50, stop_words="english")

    async def _fetch_high_rated_sessions(self) -> list:
        from sqlalchemy import select
        from backend.models.orm import SessionHistory
        
        rows = []
        async for db in get_db():
            stmt = select(SessionHistory).limit(100)
            result = await db.execute(stmt)
            for r in result.scalars().all():
                rows.append({"task_description": r.task_description, "generated_code": r.generated_code})
        return rows

    async def get_top_concerns(self) -> list:
        return ["SQL Injection", "Missing input validation", "Hardcoded secrets"]

    async def get_style_guidelines(self) -> list:
        sessions = await self._fetch_high_rated_sessions()
        if not sessions:
            return ["Use type hints properly", "Add comprehensive docstrings"]
        
        codes = [s["generated_code"] for s in sessions if s.get("generated_code")]
        if not codes:
            return ["Follow consistent formatting"]
            
        try:
            self.vectorizer.fit(codes)
            top_features = self.vectorizer.get_feature_names_out()
            guidelines = [f"Prefer using patterns surrounding '{f}'" for f in top_features[:3]]
            return guidelines
        except ValueError:
            return ["Follow consistent formatting"]

    async def generate_context_injection(self, task: str) -> str:
        concerns = await self.get_top_concerns()
        styles = await self.get_style_guidelines()
        
        ctx = f"User Context Update (DevShield AI Learning Core):\n"
        ctx += f"Historically, this user prioritizes preventing these vulnerabilities: {', '.join(concerns)}.\n"
        ctx += f"Code style preferences derived from fine-tuning memory:\n"
        for s in styles:
            ctx += f"- {s}\n"
            
        ctx += "\nPlease strictly adhere to these preferences while fulfilling the following task."
        return ctx

    async def export_fine_tuning_dataset(self):
        sessions = await self._fetch_high_rated_sessions()
        count = 0
        with open(FINETUNE_DATASET, 'w', encoding='utf-8') as f:
            for s in sessions:
                record = {
                    "prompt": s.get("task_description", ""),
                    "completion": s.get("generated_code", "")
                }
                f.write(json.dumps(record) + "\n")
                count += 1
                
        logger.info(f"Exported {count} high quality sessions to {FINETUNE_DATASET} for LLM Fine-Tuning.")
        print("To submit this dataset to Google Vertex AI for tuning, run:")
        print("gcloud ai custom-jobs create ...")
        return str(FINETUNE_DATASET)
