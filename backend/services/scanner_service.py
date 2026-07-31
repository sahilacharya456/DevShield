import structlog
from typing import Dict, Any
from backend.models.database import get_db
from backend.models.orm import Scan
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
