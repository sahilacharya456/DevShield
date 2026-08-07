import structlog
from typing import Dict, Any
from backend.models.database import get_db
from backend.models.orm import Scan, Project, User
from fastapi import HTTPException, status
from backend.worker import scan_repository_task

logger = structlog.get_logger()

class ScannerService:
    """
    Service layer abstraction for security scanning operations.
    """
    
    @staticmethod
    async def trigger_scan(project_id: int, user_id: int) -> Dict[str, Any]:
        """Creates a Scan record and triggers the Celery worker."""
        async for db in get_db():
            # Validate ownership (Fix IDOR)
            from sqlalchemy.future import select
            user = await db.get(User, user_id)
            stmt = select(Project).where(Project.id == project_id, Project.organization_id == user.organization_id)
            result = await db.execute(stmt)
            project = result.scalars().first()
            if not project:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project not found or access denied")

            scan = Scan(
                project_id=project_id,
                status="PENDING",
                scan_type="SAST"
            )
            db.add(scan)
            await db.commit()
            await db.refresh(scan)
            
            # Dispatch Celery task
            task = scan_repository_task.delay(scan.id, project_id, user_id)
            
            return {
                "scan_id": scan.id,
                "task_id": task.id,
                "status": scan.status
            }
