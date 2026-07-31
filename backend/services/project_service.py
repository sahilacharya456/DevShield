import structlog
from typing import Dict, Any, List
from sqlalchemy.future import select
from sqlalchemy import func
from backend.models.database import get_db
from backend.models.orm import Project, User, Scan

logger = structlog.get_logger()

class ProjectService:
    """
    Service layer for project management and repository operations.
    """
    
    @staticmethod
    async def get_project(project_id: int, user_id: int) -> Dict[str, Any]:
        """Fetch project details."""
        async for db in get_db():
            user = await db.get(User, user_id)
            if not user:
                return {}
            stmt = select(Project).where(Project.id == project_id, Project.organization_id == user.organization_id)
            result = await db.execute(stmt)
            project = result.scalars().first()
            if not project:
                return {}
            return {
                "id": project.id,
                "name": project.name,
                "language": project.language,
                "repo_url": project.repo_url,
                "created_at": project.created_at
            }
            
    @staticmethod
    async def get_all_projects(user_id: int) -> List[Dict[str, Any]]:
        async for db in get_db():
            user = await db.get(User, user_id)
            if not user:
                return []
            
            # Fetch projects with their latest scan data
            stmt = select(Project).where(Project.organization_id == user.organization_id)
            result = await db.execute(stmt)
            projects = result.scalars().all()
            
            project_data = []
            for p in projects:
                scan_stmt = select(Scan).where(Scan.project_id == p.id).order_by(Scan.created_at.desc()).limit(1)
                scan_res = await db.execute(scan_stmt)
                latest_scan = scan_res.scalars().first()
                
                project_data.append({
                    "id": p.id,
                    "name": p.name,
                    "language": p.language,
                    "repo_url": p.repo_url,
                    "created_at": p.created_at,
                    "score": latest_scan.overall_score if latest_scan else 100,
                    "vulns": latest_scan.vulnerabilities_found if latest_scan else 0
                })
            return project_data
        
    @staticmethod
    async def create_project(name: str, language: str, user_id: int, repo_url: str = "") -> Dict[str, Any]:
        """Create a new project record."""
        async for db in get_db():
            user = await db.get(User, user_id)
            if not user:
                raise Exception("User not found")
            new_proj = Project(
                name=name,
                language=language,
                repo_url=repo_url,
                organization_id=user.organization_id
            )
            db.add(new_proj)
            await db.commit()
            await db.refresh(new_proj)
            return {
                "id": new_proj.id,
                "name": new_proj.name,
                "language": new_proj.language,
                "repo_url": new_proj.repo_url,
                "created_at": new_proj.created_at
            }
