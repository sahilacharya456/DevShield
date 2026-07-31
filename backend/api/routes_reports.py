from fastapi import APIRouter, Response, Query
from pydantic import BaseModel
from typing import Optional, List
import io
from datetime import datetime, timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

router = APIRouter()

@router.get("/download")
async def download_report(
    project_name: str = Query(default="Your Project"),
    risk_level: str = Query(default="Medium"),
    critical_count: int = Query(default=0),
    high_count: int = Query(default=0),
    medium_count: int = Query(default=0),
):
    """
    Generates a dynamic PDF executive security report based on real scan parameters.
    """
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header Background
    p.setFillColor(colors.HexColor("#050912"))
    p.rect(0, height - 120, width, 120, fill=1, stroke=0)
    
    # Title
    p.setFont("Helvetica-Bold", 22)
    p.setFillColor(colors.HexColor("#3b82f6"))
    p.drawString(50, height - 55, "DevShield AI X")
    p.setFont("Helvetica", 14)
    p.setFillColor(colors.HexColor("#94a3b8"))
    p.drawString(50, height - 75, "Executive Security Audit Report")
    
    # Report meta
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    p.setFont("Helvetica", 10)
    p.setFillColor(colors.HexColor("#64748b"))
    p.drawString(50, height - 100, f"Generated: {now}  |  Target: {project_name}  |  Risk Level: {risk_level}")
    
    # Divider
    p.setStrokeColor(colors.HexColor("#1e293b"))
    p.setLineWidth(1)
    p.line(50, height - 130, width - 50, height - 130)
    
    # Summary Section
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(colors.HexColor("#1e293b"))
    p.drawString(50, height - 165, "Executive Summary")
    
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.black)
    text = p.beginText(50, height - 195)
    total = critical_count + high_count + medium_count
    text.textLines([
        f"DevShield AI performed a comprehensive multi-engine security analysis of '{project_name}'.",
        f"Analysis engines: Tree-Sitter SAST, OSV Analytics, Secret Neural Net, ML Anomaly Detector.",
        "",
        f"Total Vulnerabilities Found: {total}",
        f"  Critical: {critical_count}",
        f"  High: {high_count}",
        f"  Medium: {medium_count}",
        "",
        "Remediation: DevShield Auto-Fix LLM has generated secure patch recommendations.",
        "Please review the Auto-Fix Studio to apply AI-generated patches.",
    ])
    p.drawText(text)
    
    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.grey)
    p.drawString(50, 40, "Generated automatically by DevShield AI X — Confidential Security Report")
    p.drawString(width - 100, 40, f"Page 1")
    
    p.showPage()
    p.save()
    
    pdf = buffer.getvalue()
    buffer.close()
    
    headers = {'Content-Disposition': f'attachment; filename="devshield-{project_name}-audit.pdf"'}
    return Response(content=pdf, media_type="application/pdf", headers=headers)
