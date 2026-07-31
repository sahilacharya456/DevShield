from fastapi import APIRouter, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.models.schemas import SecurityScanRequest, SecurityScanResponse, AutoFixRequest, AutoFixResponse, StandardErrorResponse
from backend.agents.security_agent import SecurityAgent
from backend.agents.autofix_agent import AutoFixAgent

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/scan", response_model=SecurityScanResponse)
@limiter.limit("20/minute")
async def scan_code(request: Request, body: SecurityScanRequest):
    agent = SecurityAgent()
    report = await agent.analyze(body.code)
    return SecurityScanResponse(**report)

@router.post("/autofix", response_model=AutoFixResponse)
@limiter.limit("10/minute")
async def autofix_code(request: Request, body: AutoFixRequest):
    agent = AutoFixAgent()
    # Pydantic v2 format
    vulns = body.vulnerability_report.model_dump()["vulnerabilities"]
    result = await agent.fix(body.code, vulns)
    return AutoFixResponse(**result)
