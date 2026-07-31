import structlog
from sqlalchemy import select
from backend.models.database import get_db
from backend.models.orm import SessionHistory

logger = structlog.get_logger()

class SessionManager:
    async def create_session(self, user_id: int, task: str, language: str, code: str, ai_used: str, score: int) -> int:
        async for db in get_db():
            session = SessionHistory(
                user_id=user_id,
                task_description=task,
                language=language,
                generated_code=code,
                ai_used=ai_used,
                vulnerability_score=score
            )
            db.add(session)
            await db.commit()
            await db.refresh(session)
            return session.id

    async def get_history(self, user_id: int, limit: int = 10) -> list:
        async for db in get_db():
            stmt = select(SessionHistory).where(SessionHistory.user_id == user_id).order_by(SessionHistory.created_at.desc()).limit(limit)
            result = await db.execute(stmt)
            rows = result.scalars().all()
            return [
                {
                    "id": r.id,
                    "task_description": r.task_description,
                    "language": r.language,
                    "generated_code": r.generated_code,
                    "ai_used": r.ai_used,
                    "vulnerability_score": r.vulnerability_score,
                    "created_at": r.created_at
                }
                for r in rows
            ]
