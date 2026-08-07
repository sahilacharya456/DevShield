from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import List

from backend.models.database import get_db
from backend.models.orm import User, Project, Scan
from backend.models.orm import User, Project, Scan
from backend.security.auth import get_current_user

router = APIRouter()

class MetricResponse(BaseModel):
    title: str
    value: str
    trend: str
    icon: str
    color: str

class AlertResponse(BaseModel):
    title: str
    location: str
    severity: str

class DashboardResponse(BaseModel):
    metrics: List[MetricResponse]
    recent_scans: List[dict]
    soc_alerts: List[AlertResponse]

@router.get("/metrics", response_model=DashboardResponse)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Fetch DevSecOps metrics for the Command Center Dashboard.
    Fully integrated with the real PostgreSQL/SQLite DB.
    """
    # Count user's projects (Show all for admin demo)
    proj_result = await db.execute(
        select(func.count(Project.id))
    )
    project_count = proj_result.scalar() or 0
    
    # Aggregate total scans and vulnerabilities via SQL
    vuln_result = await db.execute(select(func.sum(Scan.vulnerabilities_found)))
    total_vulns = vuln_result.scalar() or 0
    
    score_result = await db.execute(select(func.avg(Scan.overall_score)))
    avg_score = score_result.scalar() or 100
    
    # Fetch only recent scans for UI
    scan_result = await db.execute(
        select(Scan, Project)
        .join(Project)
        .order_by(Scan.created_at.desc())
        .limit(4)
    )
    recent_scans_data = scan_result.all()
    
    recent_scans = []
    for s in recent_scans_data:
        score = s.Scan.overall_score
        if score >= 90:
            severity = "low"
        elif score >= 70:
            severity = "medium"
        else:
            severity = "high"
            
        recent_scans.append({
            "name": s.Project.name,
            "lang": s.Project.language,
            "score": score,
            "severity": severity,
            "time": s.Scan.created_at.strftime("%Y-%m-%d %H:%M") if s.Scan.created_at else "Just now"
        })

    # Fetch real SOC alerts efficiently
    alert_result = await db.execute(
        select(Scan, Project)
        .join(Project)
        .where(Scan.overall_score < 70)
        .order_by(Scan.created_at.desc())
        .limit(3)
    )
    alerts_data = alert_result.all()
    soc_alerts = []
    for s in alerts_data:
        soc_alerts.append({
            "title": f"Critical Vulnerability in {s.Project.name}",
            "location": f"Scan ID: {s.Scan.id}",
            "severity": "danger"
        })


    return {
        "metrics": [
            {"title": "Active Projects", "value": str(project_count), "trend": "Real-time sync", "icon": "📦", "color": "blue"},
            {"title": "Total Vulnerabilities", "value": str(total_vulns), "trend": "Detected across all repos", "icon": "🚨", "color": "danger" if total_vulns > 0 else "success"},
            {"title": "Avg Risk Score", "value": f"{int(avg_score)}/100", "trend": "Global posture", "icon": "🛡️", "color": "indigo"},
            {"title": "Auto-Fixed Issues", "value": "0", "trend": "0% fix rate (needs manual review)", "icon": "🔧", "color": "warning"},
        ],
        "recent_scans": recent_scans,
        "soc_alerts": soc_alerts
    }
